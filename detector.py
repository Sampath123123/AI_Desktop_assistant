import cv2
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path):
        self.model_path = model_path
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = YOLO(str(self.model_path))
        return self._model

    def detect(self, frame):
        detections = []
        results = self.model(frame)
        for result in results:
            for box in result.boxes:
                confidence = box.conf[0].item()
                if confidence <= 0.5:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                class_id = int(box.cls[0].item())
                label = self.model.names[class_id]
                detections.append(
                    {
                        "label": label,
                        "confidence": confidence,
                        "box": (int(x1), int(y1), int(x2 - x1), int(y2 - y1)),
                    }
                )
        return detections

    def draw_detections(self, frame, detections):
        for detection in detections:
            x, y, w, h = detection["box"]
            label = detection["label"]
            confidence = detection["confidence"]
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame,
                f"{label} {confidence:.2f}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        return frame

    def detect_from_camera(self):
        video = cv2.VideoCapture(0)
        if not video.isOpened():
            return False, [], "Camera access is unavailable."

        detected_labels = []
        try:
            while True:
                ok, frame = video.read()
                if not ok:
                    return False, detected_labels, "Failed to capture video."

                detections = self.detect(frame)
                for detection in detections:
                    if detection["label"] not in detected_labels:
                        detected_labels.append(detection["label"])

                preview = self.draw_detections(frame, detections)
                cv2.imshow("YOLO Object Detection", preview)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            video.release()
            cv2.destroyAllWindows()

        if detected_labels:
            return True, detected_labels, "I detected: " + ", ".join(detected_labels) + "."
        return True, detected_labels, "No objects were detected."
