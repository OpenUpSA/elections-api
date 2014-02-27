from sqlalchemy import Column, Integer, String, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from api import db


class VotingDistrict(db.Model):

    __tablename__ = 'voting_districts'

    # columns
    pk = Column(Integer, primary_key=True)
    voting_district_id = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)
    ward_pk = Column(Integer, ForeignKey('wards.pk'))

    # associations
    ward = relationship("Ward")

    # indexes
    Index('voting_district_year_id_ix', year, voting_district_id, unique=True)

    def __repr__(self):
        return "<VotingDistrict(pk='%s', year='%s', voting_district_id='%s')>" % (
            str(self.pk), str(self.year), str(self.voting_district_id))


class Ward(db.Model):

    __tablename__ = 'wards'

    # columns
    pk = Column(Integer, primary_key=True)
    ward_id = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)
    municipality_pk = Column(Integer, ForeignKey('municipalities.pk'))

    # associations
    municipality = relationship("Municipality")

    # indexes
    Index('ward_year_id_ix', year, ward_id, unique=True)

    def __repr__(self):
        return "<Ward(pk='%s', year='%s', ward_id='%s')>" % (
            str(self.pk), str(self.year), str(self.ward_id))


class Municipality(db.Model):

    __tablename__ = 'municipalities'

    # columns
    pk = Column(Integer, primary_key=True)
    municipality_id = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)
    province_pk = Column(Integer, ForeignKey('provinces.pk'))

    # associations
    province = relationship("Province")

    # indexes
    Index('municipality_year_id_ix', year, municipality_id, unique=True)

    def __repr__(self):
        return "<Municipality(pk='%s', year='%s', municipality_id='%s')>" % (
            str(self.pk), str(self.year), str(self.municipality_id))


class Province(db.Model):

    __tablename__ = 'provinces'

    # columns
    pk = Column(Integer, primary_key=True)
    province_id = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    results_provincial = Column(String)
    results_national = Column(String)

    # indexes
    Index('province_year_id_ix', year, province_id, unique=True)

    def __repr__(self):
        return "<Province(pk='%s', year='%s', province_id='%s')>" % (
            str(self.pk), str(self.year), str(self.province_id))