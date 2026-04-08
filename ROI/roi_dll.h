/*
 * roi_dll.h - Header for ROI processing DLL.
 *
 * Usage from C/C++:
 *   #include "roi_dll.h"
 *   int ret = ROI("C:/data/W_ROI.png", "C:/data/W128.png");
 *
 * Usage from MATLAB:
 *   loadlibrary('roi_dll.dll', 'roi_dll.h');
 *   calllib('roi_dll', 'ROI', 'C:/data/W_ROI.png', 'C:/data/W128.png');
 *   unloadlibrary('roi_dll');
 */

#ifndef ROI_DLL_H
#define ROI_DLL_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef BUILD_DLL
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT __declspec(dllimport)
#endif

/**
 * ROI - Process ROI images.
 *
 * Output files (TIF, PNG, CSV) are saved to an "out_ROI" folder
 * created next to the ROI reference image.
 *
 * @param roi_file_name  Full path to ROI reference image.
 * @param tar_file_name  Full path to target image (or glob pattern).
 * @return 0 on success, -1 on error.
 */
DLL_EXPORT int ROI(const char *roi_file_name, const char *tar_file_name);

/**
 * ROI_with_output - Process ROI images with explicit output directory.
 *
 * @param roi_file_name  Full path to ROI reference image.
 * @param tar_file_name  Full path to target image (or glob pattern).
 * @param output_dir     Full path to output directory.
 * @return 0 on success, -1 on error.
 */
DLL_EXPORT int ROI_with_output(const char *roi_file_name,
                               const char *tar_file_name,
                               const char *output_dir);

#ifdef __cplusplus
}
#endif

#endif /* ROI_DLL_H */
