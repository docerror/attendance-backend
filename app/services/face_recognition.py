# # import face_recognition
# # import numpy as np
# # import json
# # import requests
# # from io import BytesIO
# # from PIL import Image
# # from typing import List, Tuple, Optional
# # from sqlalchemy.orm import Session
# # from app.models.student import Student
# # import logging

# # logger = logging.getLogger(__name__)


# # class FaceRecognitionService:
# #     def __init__(self, tolerance: float = 0.6):
# #         """
# #         Initialize the face recognition service.
        
# #         Args:
# #             tolerance: How much distance between faces to consider it a match.
# #                       Lower is more strict. 0.6 is typical best performance.
# #         """
# #         self.tolerance = tolerance
    
# #     def _load_image_from_url(self, url: str) -> np.ndarray:
# #         """Load an image from a URL into a numpy array."""
# #         response = requests.get(url)
# #         response.raise_for_status()
# #         img = Image.open(BytesIO(response.content))
# #         return np.array(img.convert('RGB'))
    
# #     def _load_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
# #         """Load an image from bytes into a numpy array."""
# #         img = Image.open(BytesIO(image_bytes))
# #         return np.array(img.convert('RGB'))
    
# #     def extract_face_encoding(self, image_url: str) -> Optional[List[float]]:
# #         """
# #         Extract face encoding from a single-person image.
        
# #         Args:
# #             image_url: URL of the image (typically from Cloudinary)
            
# #         Returns:
# #             Face encoding as a list of floats, or None if no face found
# #         """
# #         try:
# #             image = self._load_image_from_url(image_url)
# #             face_locations = face_recognition.face_locations(image, model="hog")
            
# #             if not face_locations:
# #                 logger.warning(f"No face found in image: {image_url}")
# #                 return None
            
# #             # Use the first (largest) face found
# #             face_encodings = face_recognition.face_encodings(image, face_locations)
            
# #             if face_encodings:
# #                 return face_encodings[0].tolist()
# #             return None
            
# #         except Exception as e:
# #             logger.error(f"Error extracting face encoding: {str(e)}")
# #             return None
    
# #     def extract_faces_from_group(self, image_bytes: bytes) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
# #         """
# #         Extract all faces from a group photo.
        
# #         Args:
# #             image_bytes: The group photo as bytes
            
# #         Returns:
# #             List of (face_encoding, face_location) tuples
# #         """
# #         try:
# #             image = self._load_image_from_bytes(image_bytes)
            
# #             # Find all faces in the image
# #             face_locations = face_recognition.face_locations(image, model="hog")
# #             face_encodings = face_recognition.face_encodings(image, face_locations)
            
# #             return list(zip(face_encodings, face_locations))
            
# #         except Exception as e:
# #             logger.error(f"Error extracting faces from group: {str(e)}")
# #             return []
    
# #     def match_faces(
# #         self, 
# #         group_encodings: List[np.ndarray], 
# #         known_encodings: List[Tuple[int, np.ndarray]]
# #     ) -> List[int]:
# #         """
# #         Match faces from a group photo against known student encodings.
        
# #         Args:
# #             group_encodings: List of face encodings from the group photo
# #             known_encodings: List of (student_id, encoding) tuples
            
# #         Returns:
# #             List of matched student IDs
# #         """
# #         matched_student_ids = []
        
# #         if not known_encodings:
# #             return matched_student_ids
        
# #         known_ids = [k[0] for k in known_encodings]
# #         known_face_encodings = [np.array(k[1]) for k in known_encodings]
        
# #         for group_encoding in group_encodings:
# #             # Compare this face against all known faces
# #             distances = face_recognition.face_distance(known_face_encodings, group_encoding)
            
# #             # Find the best match
# #             if len(distances) > 0:
# #                 min_distance_idx = np.argmin(distances)
# #                 min_distance = distances[min_distance_idx]
                
# #                 if min_distance <= self.tolerance:
# #                     student_id = known_ids[min_distance_idx]
# #                     if student_id not in matched_student_ids:
# #                         matched_student_ids.append(student_id)
        
# #         return matched_student_ids
    
# #     def process_attendance(
# #         self, 
# #         db: Session, 
# #         image_bytes: bytes, 
# #         branch: str, 
# #         semester: int
# #     ) -> Tuple[List[int], int]:
# #         """
# #         Process a group photo and return matched student IDs.
        
# #         Args:
# #             db: Database session
# #             image_bytes: The group photo as bytes
# #             branch: Filter students by branch
# #             semester: Filter students by semester
            
# #         Returns:
# #             Tuple of (matched_student_ids, total_faces_detected)
# #         """
# #         # Extract faces from group photo
# #         faces_data = self.extract_faces_from_group(image_bytes)
        
# #         if not faces_data:
# #             logger.warning("No faces detected in the group photo")
# #             return [], 0
        
# #         group_encodings = [f[0] for f in faces_data]
# #         total_faces = len(group_encodings)
        
# #         # Get all students in the specified branch and semester with face encodings
# #         students = db.query(Student).filter(
# #             Student.branch == branch,
# #             Student.semester == semester,
# #             Student.face_encoding.isnot(None)
# #         ).all()
        
# #         if not students:
# #             logger.warning(f"No registered students found for {branch} - Semester {semester}")
# #             return [], total_faces
        
# #         # Prepare known encodings
# #         known_encodings = []
# #         for student in students:
# #             if student.face_encoding:
# #                 encoding = json.loads(student.face_encoding)
# #                 known_encodings.append((student.id, encoding))
        
# #         # Match faces
# #         matched_ids = self.match_faces(group_encodings, known_encodings)
        
# #         return matched_ids, total_faces


# # # Global instance
# # face_service = FaceRecognitionService()


# #chat gpt code below
# import face_recognition
# import numpy as np
# import json
# import requests
# from io import BytesIO
# from PIL import Image
# from typing import List, Tuple, Optional
# from sqlalchemy.orm import Session
# from app.models.student import Student
# import logging

# logger = logging.getLogger(__name__)


# class FaceRecognitionService:
#     def __init__(self, tolerance: float = 0.5):
#         """
#         Lower tolerance = stricter matching
#         0.5 is safer than 0.6 (reduces wrong matches)
#         """
#         self.tolerance = tolerance

#     def _load_image_from_url(self, url: str) -> np.ndarray:
#         response = requests.get(url)
#         response.raise_for_status()
#         img = Image.open(BytesIO(response.content))
#         return np.array(img.convert('RGB'))

#     def _load_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
#         img = Image.open(BytesIO(image_bytes))
#         return np.array(img.convert('RGB'))

#     # ================= SINGLE IMAGE ENCODING =================
#     def extract_face_encoding(self, image_url: str) -> Optional[List[float]]:
#         try:
#             image = self._load_image_from_url(image_url)

#             face_locations = face_recognition.face_locations(image, model="hog")

#             if not face_locations:
#                 logger.warning(f"No face found in image: {image_url}")
#                 return None

#             # ✅ Select largest face (important)
#             largest_face = max(
#                 face_locations,
#                 key=lambda box: (box[2] - box[0]) * (box[1] - box[3])
#             )

#             face_encodings = face_recognition.face_encodings(
#                 image,
#                 [largest_face],
#                 num_jitters=2
#             )

#             if face_encodings:
#                 return face_encodings[0].tolist()

#             return None

#         except Exception as e:
#             logger.error(f"Error extracting encoding: {e}")
#             return None

#     # ================= GROUP IMAGE =================
#     def extract_faces_from_group(
#         self,
#         image_bytes: bytes
#     ) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:

#         try:
#             image = self._load_image_from_bytes(image_bytes)

#             face_locations = face_recognition.face_locations(image, model="hog")

#             face_encodings = face_recognition.face_encodings(
#                 image,
#                 face_locations,
#                 num_jitters=2   # ✅ improves stability
#             )

#             return list(zip(face_encodings, face_locations))

#         except Exception as e:
#             logger.error(f"Error extracting faces: {e}")
#             return []

#     # ================= MATCHING =================
#     def match_faces(
#         self,
#         group_encodings: List[np.ndarray],
#         known_encodings: List[Tuple[int, np.ndarray]]
#     ) -> List[int]:

#         matched_student_ids = []
#         used_students = set()  # prevent duplicate assignment

#         if not known_encodings:
#             return matched_student_ids

#         known_ids = [k[0] for k in known_encodings]
#         known_face_encodings = [np.array(k[1]) for k in known_encodings]

#         for group_encoding in group_encodings:

#             distances = face_recognition.face_distance(
#                 known_face_encodings,
#                 group_encoding
#             )

#             if len(distances) == 0:
#                 continue

#             sorted_indices = np.argsort(distances)

#             best_idx = sorted_indices[0]
#             best_distance = distances[best_idx]

#             # ✅ SECOND BEST CHECK (very important)
#             if len(sorted_indices) > 1:
#                 second_distance = distances[sorted_indices[1]]

#                 # If both are too close → skip (avoid confusion)
#                 if abs(second_distance - best_distance) < 0.04:
#                     continue

#             # ✅ STRICT MATCH
#             if best_distance <= self.tolerance:
#                 student_id = known_ids[best_idx]

#                 if student_id not in used_students:
#                     matched_student_ids.append(student_id)
#                     used_students.add(student_id)

#         return matched_student_ids

#     # ================= MAIN FUNCTION =================
#     def process_attendance(
#         self,
#         db: Session,
#         image_bytes: bytes,
#         branch: str,
#         semester: int
#     ) -> Tuple[List[int], int]:

#         faces_data = self.extract_faces_from_group(image_bytes)

#         if not faces_data:
#             logger.warning("No faces detected")
#             return [], 0

#         group_encodings = [f[0] for f in faces_data]
#         total_faces = len(group_encodings)

#         students = db.query(Student).filter(
#             Student.branch == branch,
#             Student.semester == semester,
#             Student.face_encoding.isnot(None)
#         ).all()

#         if not students:
#             logger.warning(f"No students found for {branch} Sem {semester}")
#             return [], total_faces

#         known_encodings = []

#         for student in students:
#             try:
#                 encoding = json.loads(student.face_encoding)
#                 known_encodings.append((student.id, encoding))
#             except Exception as e:
#                 logger.warning(f"Invalid encoding for student {student.id}")
#                 continue

#         matched_ids = self.match_faces(group_encodings, known_encodings)

#         return matched_ids, total_faces


# # Global instance
# face_service = FaceRecognitionService()


#Below code is used to fix the deployment app crash issue 
import numpy as np
import json
import requests
from io import BytesIO
from PIL import Image
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.student import Student
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    def __init__(self, tolerance: float = 0.5):
        """
        Lower tolerance = stricter matching
        """
        self.tolerance = tolerance

    # ================= LAZY LOADER (IMPORTANT FIX) =================
    def _fr(self):
        import face_recognition
        return face_recognition

    # ================= IMAGE LOADERS =================
    def _load_image_from_url(self, url: str) -> np.ndarray:
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return np.array(img.convert('RGB'))

    def _load_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(BytesIO(image_bytes))
        return np.array(img.convert('RGB'))

    # ================= SINGLE IMAGE ENCODING =================
    def extract_face_encoding(self, image_url: str) -> Optional[List[float]]:
        try:
            fr = self._fr()   # ✅ SAFE IMPORT HERE

            image = self._load_image_from_url(image_url)

            face_locations = fr.face_locations(image, model="hog")

            if not face_locations:
                logger.warning(f"No face found in image: {image_url}")
                return None

            # largest face selection (unchanged logic)
            largest_face = max(
                face_locations,
                key=lambda box: (box[2] - box[0]) * (box[1] - box[3])
            )

            face_encodings = fr.face_encodings(
                image,
                [largest_face],
                num_jitters=2
            )

            if face_encodings:
                return face_encodings[0].tolist()

            return None

        except Exception as e:
            logger.error(f"Error extracting encoding: {e}")
            return None

    # ================= GROUP IMAGE =================
    def extract_faces_from_group(
        self,
        image_bytes: bytes
    ) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:

        try:
            fr = self._fr()   # ✅ SAFE IMPORT HERE

            image = self._load_image_from_bytes(image_bytes)

            face_locations = fr.face_locations(image, model="hog")

            face_encodings = fr.face_encodings(
                image,
                face_locations,
                num_jitters=2
            )

            return list(zip(face_encodings, face_locations))

        except Exception as e:
            logger.error(f"Error extracting faces: {e}")
            return []

    # ================= MATCHING =================
    def match_faces(
        self,
        group_encodings: List[np.ndarray],
        known_encodings: List[Tuple[int, np.ndarray]]
    ) -> List[int]:

        fr = self._fr()   # ✅ SAFE IMPORT HERE

        matched_student_ids = []
        used_students = set()

        if not known_encodings:
            return matched_student_ids

        known_ids = [k[0] for k in known_encodings]
        known_face_encodings = [np.array(k[1]) for k in known_encodings]

        for group_encoding in group_encodings:

            distances = fr.face_distance(
                known_face_encodings,
                group_encoding
            )

            if len(distances) == 0:
                continue

            sorted_indices = np.argsort(distances)

            best_idx = sorted_indices[0]
            best_distance = distances[best_idx]

            # second best check (unchanged logic)
            if len(sorted_indices) > 1:
                second_distance = distances[sorted_indices[1]]

                if abs(second_distance - best_distance) < 0.04:
                    continue

            if best_distance <= self.tolerance:
                student_id = known_ids[best_idx]

                if student_id not in used_students:
                    matched_student_ids.append(student_id)
                    used_students.add(student_id)

        return matched_student_ids

    # ================= MAIN FUNCTION =================
    def process_attendance(
        self,
        db: Session,
        image_bytes: bytes,
        branch: str,
        semester: int
    ) -> Tuple[List[int], int]:

        faces_data = self.extract_faces_from_group(image_bytes)

        if not faces_data:
            logger.warning("No faces detected")
            return [], 0

        group_encodings = [f[0] for f in faces_data]
        total_faces = len(group_encodings)

        students = db.query(Student).filter(
            Student.branch == branch,
            Student.semester == semester,
            Student.face_encoding.isnot(None)
        ).all()

        if not students:
            logger.warning(f"No students found for {branch} Sem {semester}")
            return [], total_faces

        known_encodings = []

        for student in students:
            try:
                encoding = json.loads(student.face_encoding)
                known_encodings.append((student.id, encoding))
            except Exception:
                logger.warning(f"Invalid encoding for student {student.id}")
                continue

        matched_ids = self.match_faces(group_encodings, known_encodings)

        return matched_ids, total_faces


# Global instance
face_service = FaceRecognitionService()