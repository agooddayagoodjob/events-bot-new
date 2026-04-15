from __future__ import annotations

import numpy as np

from video_announce import poller


def test_video_thumbnail_input_builds_jpeg_from_first_frame(monkeypatch):
    frame = np.zeros((4, 4, 3), dtype=np.uint8)

    class _Cap:
        def isOpened(self) -> bool:
            return True

        def read(self):
            return True, frame

        def release(self) -> None:
            return None

    class _Cv2:
        IMWRITE_JPEG_QUALITY = 1

        @staticmethod
        def VideoCapture(path):  # noqa: ANN001
            return _Cap()

        @staticmethod
        def imencode(ext, img, params):  # noqa: ANN001
            assert ext == ".jpg"
            assert img is frame
            assert params == [1, 95]
            return True, np.frombuffer(b"jpeg-data", dtype=np.uint8)

    monkeypatch.setattr(poller, "cv2", _Cv2)

    thumb = poller._video_thumbnail_input("/tmp/cherryflash.mp4")

    assert thumb is not None
    assert thumb.filename == "cherryflash_thumb.jpg"
    assert thumb.data == b"jpeg-data"
