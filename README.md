# 快捷标注助手 - ShortLabel

## 简介 - Introduction
快捷标注助手秉持所有操作均可使用快捷键完成的理念，大幅提高效率。

包含功能有：
- 视频追踪：基于opencv的视频追踪来生成标注框。

GUI界面采用pyqt6制作。

ShortLabel is an application for labeling video.
All operations can use the shortcuts to improve efficiency.

Including:
- Video tracking: based on opencv tracking method to generate label box.

GUI is based on PyQt6.

## 更新 - Update
参见[Changelog](./Changelog.md)。

See [Changelog](./Changelog.md).

## 安装 - Installation
- 安装Python，版本>=3.9。
- 在当前文件夹中，使用如下命令安装依赖库：
```
pip install -r ./Conf/requirements.txt
```
- 安装完成后点击[ShortLabel.cmd](./ShortLabel.cmd)启动应用。

---

- Install Python>=3.9.
- In current workfolder, use command below to install dependence:
```
pip install -r ./Conf/requirements.txt
```
- Launch application via [ShortLabel.cmd](./ShortLabel.cmd).


## 操作 - Operation Guide
- 打开视频：<kbd>Ctrl+O</kbd>。选择视频文件，会在视频所在文件夹生成标注和图片。
- 视频导航：
    - 下一张：<kbd>D</kbd>，导航到下一张视频帧，在跳帧数输入框中修改跳帧数可更快的跳跃。
    - 上一张：<kbd>A</kbd>，导航到上一张视频帧，受跳帧数影响。
    - 播放：<kbd>Space</kbd>，开始自动播放/停止视频。受跳帧数影响，追踪器生效。
    - 拖动进度条：不受跳帧影响，追踪器不生效。
    - 键入帧：在帧数输入框输入指定帧可快速跳跃，追踪器生效。
- 标注：创建标注框之前，可在右侧标签列表中选择标签。
    - 新建：按下<kbd>E</kbd>后，在图片上点击一下出现待选框，再点击一下完成框选标注。
    - 移动：鼠标<kbd>左键</kbd>拖动标注框。
    - 更换标签：在标注框上<kbd>右键</kbd>弹出待选标签列表，点选更改。
    - 更改大小：拖动标注框右下角的小方块。
- 保存：<kbd>S</kbd>。已保存的图片和标注会放在视频所在文件夹下，与视频文件同名。格式参考Yolo。
    - 标注有改动的图片，未保存的边框为黄色。
    - 已保存的图片边框为绿色。
    - 已校对的图片边框为蓝色。
- 追踪器：在创建追踪器之前，可在菜单栏中更换追踪方法，右侧标签列表中选择标签。
    - 新建：按下<kbd>T</kbd>后，在图片上点击一下出现待选框，再点击一下完成追踪器创建。
    - 启用/禁用：在右侧追踪器列表中勾选/取消，或按<kbd>G</kbd>。
    - 采纳：点击追踪器后，按<kbd>Q</kbd>生成对应标签的标注框。
    - 全部采纳：按<kbd>F</kbd>生成全部追踪器的标注框。
- 删除：点击激活标注框或追踪器，按下<kbd>X</kbd>删除。
- 选项：
    - 切换显示：按下<kbd>Tab</kbd>会依次在显示标注和追踪器、仅显示标注、仅显示追踪器和都不显示间切换。
    - 校对模式：该模式中，前后导航将直接前往前一张、后一张有标注的图片，且追踪器不生效。
    - 自动保存：激活该模式中，按前后导航将直接保存当前图片和标注。
    - 裁剪模式：
    激活后会出现裁剪框。
    在该模式下只会保存裁剪框内的图片。
    拖动左上角和右下角的手柄缩放，拖动中上部的手柄整体移动裁剪框。
    或在右侧高级选项卡中精确修改裁剪框的大小。
    - 优先显示保存的图片：
    裁剪框是可以移动的，这就意味着当前裁剪框内的部分可能不一定是图片中所保存的内容。
    激活该选项以直接读取和查看已保存的图片。

---
- Open Video: <kbd>Ctrl+O</kbd>. Select video file, then the labels and images will be placed at the folder where the video locates.
- Video navigation:
    - Next image: <kbd>D</kbd>. Navigate to next image. Set the skip frame value(SFV) for faster navigation.
    - Previous image: <kbd>A</kbd>. Navigate to Previous image. SFV will affect this function.
    - Play video: <kbd>Space</kbd>. Play/Pause video. SFV affected. Tracker applied.
    - Drag time bar: SFV not affected. Tracker not applied.
    - Input frame: Input specific frame to jump to. Tracker applied.
- Label: Before creating the label box, the label can be changed at the label list in the right.
    - Create: Press <kbd>E</kbd>, then click first time at image, and drag the box then click the second time.
    - Move: <kbd>LMB</kbd> for dragging.
    - Change label: Pressing <kbd>RMB</kbd> on label box will show the list of labels.
    - Resize: Drag the handle at the right bottom corner of the label box.
- Save: <kbd>S</kbd>. Saved labels and images will be placed at where the video with the same name folder.
    - The border of unsaved image is yellow.
    - The border of saved image is green.
    - The border of verified image is cyan.
- Tracker: Before creating tracker, track method can be changed at menubar while label at right list.
    - Create: Press <kbd>T</kbd>, then click first time at image, and drag the box then click the second time.
    - Enable/disable: Check or not check in the right tracker list.
    - Acept: After click tracker box, press <kbd>Q</kbd> to generate label box.
    - Acept all: Press <kbd>Y</kbd> to generate label boxes of all trackers on the image.
- Delete: Press <kbd>X</kbd> after click label box or tracker box.
- Verify mode: Activate verify mode in the edit menu. In the mode, Navagation will directly goto previous/next labeled image. Tracker not applied.
- Autosave mode: Activate autosave mode in the edit menu. In this mode, navigating to other image will immediately save current labels.


# 其他 - Others
作者：Mota - leemota@hotmail.com。

开源协议：GPL 3.0。
