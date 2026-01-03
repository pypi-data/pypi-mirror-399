from typing import Self
from PySide6 import QtWidgets, QtCore
import sqlalchemy
from sqlalchemy import Column, Integer, String, Float, ARRAY, BLOB, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib

Base = declarative_base()


class Image(Base):
    __tablename__ = "__image"
    id = Column(Integer, primary_key=True)
    image_path = Column(String)
    size = Column(String)
    data = Column(BLOB)
    hash = Column(String)

    @staticmethod
    def calHash(binary_data):
        return hashlib.sha256(binary_data).hexdigest()


class Annotation(Base):
    __tablename__ = "__annotation"
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("__image.id"))
    range = Column(String)
    keypoints = Column(String)
    label = Column(String)


class Dataset:
    def __init__(self, db_path=":memory:"):
        """初始化Dataset，连接到SQLite数据库，并创建所有表。"""
        self.engine = sqlalchemy.create_engine(f"sqlite:///{db_path}", echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=True, future=True)
        self.session: sqlalchemy.orm.Session = self.Session()

    def add_image(self, image_path, data, size=None):
        """添加Image到数据库，自动计算hash。如果图片hash存在则不添加。"""
        hash_val = Image.calHash(data)
        img = self.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash_val))
        if img is None:
            image = Image(image_path=image_path, data=data, size=size, hash=hash_val)
            self.session.add(image)
            self.session.commit()
            return image
        return img

    def get_image_by_hash(self, hash_val):
        """根据hash获取图片，如果不存在返回None。"""
        return self.session.scalar(sqlalchemy.select(Image).where(Image.hash == hash_val))

    def get_image_by_id(self, image_id):
        """通过image id获得image，如果不存在返回None。"""
        return self.session.query(Image).filter_by(id=image_id).first()

    def add_annotation(self, image_id, rng, label,keypoints="[]"):
        """添加标注数据到数据库。"""
        annotation = Annotation(image_id=image_id, range=rng, label=label, keypoints=keypoints)
        self.session.add(annotation)
        self.session.commit()
        return annotation

    def get_annotations_for_image(self, image_id)->list[Annotation]:
        """获取指定image_id的所有标注。"""
        return self.session.query(Annotation).filter_by(image_id=image_id).all()

    def delete_annotation(self, annotation_id):
        """通过id删除标注。"""
        ann = self.session.query(Annotation).filter_by(id=annotation_id).first()
        if ann:
            self.session.delete(ann)
            self.session.commit()
            return True
        return False

    def update_annotation(self, annotation_id, rng=None, label=None, keypoints=None):
        """更新标注数据。"""
        ann = self.session.query(Annotation).filter_by(id=annotation_id).first()
        if ann:
            if rng is not None:
                ann.range = rng
            if label is not None:
                ann.label = label
            if keypoints is not None:
                ann.keypoints = keypoints
            self.session.commit()
            return True
        return False

    def close(self):
        """关闭数据库会话。"""
        self.session.close()

    def get_all_images(self):
        """获取所有图片。"""
        return self.session.query(Image).all()

    def get_all_annotations(self):
        """获取所有标注。"""
        return self.session.query(Annotation).all()
