# Changelog

<!--next-version-placeholder-->

## v1.1.11
### Enhancements
- Increase log file size to 50MB

## v1.1.10
### Enhancements
- remove visualization scripts and font
- remove pillow package

## v1.1.8
### Enhancements
- Add thread pool executors to handle redis requests
- Add redis frame TTL

## v1.1.7
### Fix
- Revert deletion of redis frames which caused issue with multiple consumers

## v1.1.6
### Fix
- Fix bug with importing nonexisted data structures

## v1.1.5
### Enhancements
- Redis frames are deleted once pulled to avoid processing twice
- New data structures have been added (RQueue) to improve performance
- Add new constant variables

## v1.1.4
### Enhancements
- add available devices in the AARCH64 architecture

## v1.1.3
### Enhancements
- remove opencv-contrib-python and update opencv-python-headless to 4.10.0

## v1.1.2
### Enhancements
- upgrade opencv version to 4.10.0
### Features
- add new modules in constants.modules
- add publish key values in the constants.constants

## v1.0.8
### Fix
- fix issue - cannot find video-feed when using video-feed-ip(usb, videofile) source
### Enhancements
- updated documents
### Features
- add new modules in constants.modules

## v1.0.7
### Fix
- inherit viso_data.meta object

## v1.0.6
### Fix
- standard TensorRT spell as lowercase() -> tensorrt

## v1.0.5
### Fix
- indicate numpy version for fixing - ImportError: numpy.core.multiarray failed to import

## v1.0.4
### Fix
- viso_data.meta.source.update() - Fix attribute error when new attribute comes

## v1.0.2
### Enhancements
- viso_data() - split into sub dataclasses MetaSource(), MetaModule(), MetaFrameFormat()

## v1.0.1
### Enhancements
- viso_data(), default version is set 1
### Features
- integrate viso_data into redis_utils
### Fix
- status_logger using new redis_utils
- redis_wrapper decoding bytes to str

## v1.0.0 = v0.2.15

## v0.2.15
### Features
- soft merge redis_meta with redis_encoding

## v0.2.14
### Enhancements
- add instance object for detection result
### Fix
- indicate proper paho-mqtt version

## v0.2.12/v0.2.13
### Enhancements
- add member functions into __init__.py (redis and mqtt)
### Fix
- remove func redis_wrapper.gen_redis_key_status()

## v0.2.11
### Enhancements
- remove pillow version

## v0.2.10
### Enhancements
- update to python3.10

## v0.2.9
### Enhancements
- more detailed visualization parameters

## v0.2.7(v0.2.8)
### Enhancements
- constants - add common keys for object tracking/recognition
- visualization:
  - add draw_tracking_objects
  - ignore empty object lists on visualization function

## v0.2.6
### Fix
- update other viz functions (vis_obj, vis_roi) using updated utils.put_text()

## v0.2.5
### Fix
- update function to calculate padding in the case of multi-line text
- add new framework TensorRT
- update utils.put_text() parameter names

## v0.2.4
### Features
- sphinx autodoc

## v0.2.3
### Features
- added drawer function for (line-type) roi objects
### Fix
- visualize.utils.put_text() - correct padding calculation
- visualize.utils.put_text() - treat multi-line text too
- visualize.utils.put_text() - added option for center align

## v0.2.2
### Features
- new declaration of modules
### Fix
- VizObj, VizRoi - missed arguments (text_color)
- update default shadow_color with pillow RGBA format(255, 0, 0, 255) = RED

## v0.2.1
### Fix
- update default shadow_color with pillow RGBA format(255, 0, 0, 255) = RED

## v0.2.0
### Features
- new declaration of modules
- added CHANGELOG.md
### Fix
- VizObj, VizRoi - missed arguments (text_color)
- alpha channel value type, float to integer

## v0.1.3
### Enhancements
- Update visualization for dynamic fonts
### Fix
- init_font() - the case of not existing font_name

## v0.1.2
### Enhancements
- upgrade opencv version to 4.6.0
### Fix
- fix font_path

## v0.1.0
### Fix
- fix color order from BGR to RGB
