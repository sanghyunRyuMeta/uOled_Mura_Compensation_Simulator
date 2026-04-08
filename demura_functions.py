import ctypes
import numpy as np
import pandas as pd
from time import time
import json
import os
import shutil
from ctypes import POINTER, c_double, c_int

class Meta_Demura:
    def __init__(self, config):
        self.config = config
        self.mode = config.get("mode", "RGB").upper()

        # --- Set meta_types automatically based on mode ---
        if self.mode == "WHITE":
            self.meta_types = ["W32", "W128"]
        elif self.mode == "RGB":
            self.meta_types = ["Red32", "Green32", "Blue32",
                               "Red128", "Green128", "Blue128"]
        else:
            raise ValueError(f"Unsupported mode: {self.mode}. Must be 'WHITE' or 'RGB'.")

        # DLL setup — DeMLA preprocessing (optional)
        self.use_demla = bool(config.get('deMLA', ''))
        if self.use_demla:
            self.prepro = ctypes.WinDLL(config['deMLA']).demura_prepro
            self.prepro.argtypes = [POINTER(c_double), c_int, c_int]
            self.prepro.restype = None
        else:
            self.prepro = None

        # NOTE: Meta_DMR.dll is commented out due to missing dependencies.
        # Uncomment after installing Visual Studio Community with "Desktop development with C++" workload.
        # self.Meta_dll = ctypes.CDLL(config['Meta_dll_path']).Meta_dll
        # self.Meta_dll.argtypes = [POINTER(POINTER(POINTER(POINTER(c_double))))]
        # self.Meta_dll.restype = ctypes.c_bool
        self.Meta_dll = None  # Placeholder when DLL is unavailable

        self.nvtdll = ctypes.CDLL(config['NVTDLLPath'])
        self.nvtdll.genNVTDemuraBinArrayFile.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        self.nvtdll.genNVTDemuraBinArrayFile.restype = ctypes.c_int

        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel32.WritePrivateProfileStringW.argtypes = [
            ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_wchar_p
        ]

    def numpy_to_ctypes_4d(self, array):
        d1, d2, h, w = array.shape
        array_ctype = (POINTER(POINTER(POINTER(c_double))) * d1)()
        for i in range(d1):
            array_ctype[i] = (POINTER(POINTER(c_double)) * d2)()
            for j in range(d2):
                array_ctype[i][j] = (POINTER(c_double) * h)()
                for k in range(h):
                    array_ctype[i][j][k] = array[i][j][k].ctypes.data_as(POINTER(c_double))
        return array_ctype

    def read_csv(self, panel):
        """Read CSV data depending on mode (White or RGB)."""
        # Use data_dir from config to build the correct path
        data_dir = self.config.get('data_dir', './data')
        path_prefix = os.path.join(data_dir, panel)
        data = np.zeros((5, 3, 2288, 2412), dtype=np.float64)

        if self.mode == "WHITE":
            for idx, meta in enumerate(self.meta_types):  # ["W32", "W128"]
                csv_path = os.path.join(path_prefix, f'{meta}.csv')
                arr = pd.read_csv(csv_path, header=None).to_numpy()
                rs, cs = arr.shape
                arr = np.reshape(arr, (1, rs * cs))
                inout = arr.ctypes.data_as(POINTER(c_double))
                s_time = time()
                if self.prepro is not None:
                    self.prepro(inout, rs, cs)
                    print(f"|---- DeMLA_{meta}.csv Done: {time() - s_time:.4f}s")
                else:
                    print(f"|---- DeMLA skipped for {meta}.csv (no DeMLA DLL selected)")
                out = np.ctypeslib.as_array(inout, shape=(rs, cs))
                data[idx, 0, :, :] = out  # Store in channel 0


                out_path = os.path.join(path_prefix, f'{meta}_AfterDeMLA.csv')
                pd.DataFrame(out).to_csv(out_path, header=False, index=False)
                print(f"     └─ Saved processed data: {out_path}")
        else:
            channel_map = {"Red": 0, "Green": 1, "Blue": 2}
            for meta in self.meta_types:
                for color in channel_map:
                    if meta.startswith(color):
                        c = channel_map[color]
                        break
                lumi_level = int(''.join(filter(str.isdigit, meta)))
                k = 0 if lumi_level == 32 else 1
                csv_path = os.path.join(path_prefix, f'{meta}.csv')
                arr = pd.read_csv(csv_path, header=None).to_numpy()
                rs, cs = arr.shape
                arr = np.reshape(arr, (1, rs * cs))
                inout = arr.ctypes.data_as(POINTER(c_double))
                s_time = time()
                if self.prepro is not None:
                    self.prepro(inout, rs, cs)
                    print(f"|---- DeMLA_{meta}.csv Done: {time() - s_time:.4f}s")
                else:
                    print(f"|---- DeMLA skipped for {meta}.csv (no DeMLA DLL selected)")
                out = np.ctypeslib.as_array(inout, shape=(rs, cs))
                data[k, c, :, :] = out


                out_path = os.path.join(path_prefix, f'{meta}_AfterDeMLA.csv')
                pd.DataFrame(out).to_csv(out_path, header=False, index=False)
                print(f"     └─ Saved processed data: {out_path}")

        return data

    def genNVTDemuraInit(self, ini_file):
        result = self.nvtdll.genNVTDemuraInit(ini_file)
        if result:
            print(f"{ini_file} Successfully loaded")
        else:
            print("Failed to load the .ini file")

    def setNVTDemuraLvData2D(self, c, lumiLevel, data2D, dbvidx):
        result = self.nvtdll.setNVTDemuraLvData2D(c, lumiLevel, data2D, dbvidx)
        if result:
            print("Successfully converted 4D data to 2D")
        else:
            print("Failed to convert 4D data to 2D")

    def generate_nvtdemura_bin_array_file(self, ini_file, output_name):
        try:
            result = self.nvtdll.genNVTDemuraBinArrayFile(ini_file, output_name)
            if result != 0:
                print(f"Error generating files, return code: {result}")
                return False
            else:
                print(f"Successfully generated {output_name}.mcr and {output_name}.bin")
                return True
        except OSError as e:
            print(f"Caught an OSError: {e}")
            return False

    def modify_ini_file(self, section, key, value, ini_file):
        result = self.kernel32.WritePrivateProfileStringW(section, key, value, ini_file)
        if result:
            print(f"{key} path Successfully updated")
        else:
            print("Failed to update")
    def move_files(self, source_dir, destination_dir):
        os.makedirs(destination_dir, exist_ok=True)
        for filename in os.listdir(source_dir):
            if filename.lower().endswith('.mcr') or filename.lower().endswith('.txt') or filename.lower().endswith('.bmp') :
                src_path = os.path.join(source_dir, filename)
                dst_path = os.path.join(destination_dir, filename)
                shutil.move(src_path, dst_path)

    def run(self):
        f_time = time()
        panel = self.config['panel']
        config_file = self.config['ini_file']
        out_dir = self.config['output_dir']
        out_dir_2 = self.config.get('output_dir_2', out_dir)
        src_dir = self.config['source_dir']

        print(f"Running Meta_Demura in {self.mode} mode...")
        print(f"Using meta_types: {self.meta_types}\n")

        # Step 1: Read and preprocess CSV data
        s_time = time()
        data = self.read_csv(panel)
        print('Data Shape:', data.shape)
        img_ctypes = self.numpy_to_ctypes_4d(data)
        print(f"|---- Read CSV Data Done: {time() - s_time:.4f}s")

        # Step 2: Meta DLL
        s_time = time()
        # NOTE: Meta_dll is disabled due to missing dependencies.
        # Uncomment after installing Visual Studio Community with "Desktop development with C++" workload.
        if self.Meta_dll is not None:
            self.Meta_dll(img_ctypes)
            print(f"\n|---- Meta DLL Done: {time() - s_time:.4f}s")
        else:
            print(f"\n|---- Meta DLL Skipped (DLL not loaded): {time() - s_time:.4f}s")

        # Step 3: Demura Process
        print(f"\n|---- Demura Process ({self.mode} Mode) ---- |\n")
        self.modify_ini_file("PanelInform", "dataFolder", f"./{panel}", config_file)
        self.genNVTDemuraInit(config_file)

        s_time = time()

        if self.mode == "WHITE":
            for k in range(2):
                for c in range(1):
                    data_2d = img_ctypes[k][c]
                    lumiLevel = int(''.join(filter(str.isdigit, self.meta_types[k + c])))
                    c = c + 2
                    print(f'setNVTDemuraLvData2D: {c}, {lumiLevel}')
                    self.setNVTDemuraLvData2D(c, lumiLevel, data_2d, 0)
        else:
            colorNum = 3
            for k in range(2):
                for c in range(colorNum):
                    data_2d = img_ctypes[k][c]
                    lumi_level = int(''.join(filter(str.isdigit, self.meta_types[k * colorNum + c])))
                    print(f'setNVTDemuraLvData2D: {c+1}, {lumi_level}')
                    self.setNVTDemuraLvData2D(c+1, lumi_level, data_2d, 0)

        ret = self.generate_nvtdemura_bin_array_file(config_file, out_dir_2)
        self.move_files(src_dir, out_dir)
        print('|---- NVT DLL Done:', time() - s_time)
        print('|---- Total runtime:', time() - f_time)
        return ret
