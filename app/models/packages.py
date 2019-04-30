import csv

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path

import click
from sqlalchemy import or_, UniqueConstraint
from sqlalchemy.orm import relationship

from app import db, app


def _now():
    return datetime.now(timezone.utc)


class BasePackage(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer(), autoincrement=True, primary_key=True)

    #name = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    page_views = db.Column(db.Integer(), nullable=False)
    heatmaps = db.Column(db.Integer(), nullable=False)
    session_recordings = db.Column(db.Integer(), nullable=False)
    ab_testing = db.Column(db.Integer(), nullable=False)
    ecommerce = db.Column(db.Boolean(), nullable=False)
    reports_standard = db.Column(db.Integer(), nullable=False)
    reports_power_bi = db.Column(db.Integer(), nullable=False)
    api_data_download = db.Column(db.Integer(), nullable=False)
    api_recommandations = db.Column(db.Integer(), nullable=False)
    api_data_transformation = db.Column(db.Integer(), nullable=False)
    api_index_search = db.Column(db.Integer(), nullable=False)
    api_product_360 = db.Column(db.Integer(), nullable=False)
    api_custom_searches = db.Column(db.Integer(), nullable=False)

    price = db.Column(db.Numeric(precision=65, scale=2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)


class PackageSite(BasePackage):
    __tablename__ = 'package_site'
    __bind_key__ = 'portal'

    created_at = db.Column(db.TIMESTAMP, default=_now)
    valid_until = db.Column(db.TIMESTAMP())
    #site_id = db.Column(db.Integer(), nullable=False, unique=True)
    site_id = db.Column(db.Integer(), nullable=False)
    __table_args__ = (UniqueConstraint('name', 'site_id', name='_package_name_site_id'),)
    on_expiration = db.Column(db.ForeignKey('package_template.name'), nullable=False)
    replaced_by_id = db.Column(db.ForeignKey('package_site.id'))
    replaced_by = relationship('PackageSite', uselist=False)


class PackageTemplate(BasePackage):
    __tablename__ = 'package_template'
    __bind_key__ = 'portal'

    validity_period = db.Column(db.Interval(), default=None)
    profile_id = db.Column(db.ForeignKey('partner.id'), default=None)

    on_expiration_name = db.Column(db.ForeignKey('package_template.name'), nullable=False)
    on_expiration = relationship('PackageTemplate', uselist=False)

    max_sites = db.Column(db.Integer(), default=None)

    def get_valid_until(self):
        # we use timezone.utc instead of datetime.utcnow() since we want an aware datetime object.
        if self.validity_period:
            return _now() + self.validity_period

        return None


class PackageManager:
    @staticmethod
    def list_templates(partner_id=None):
        if partner_id:
            filter_ = or_(PackageTemplate.profile_id.is_(None), PackageTemplate.profile_id == partner_id)
        else:
            filter_ = PackageTemplate.profile_id.is_(None)

        return PackageTemplate.query.filter(filter_).all()

    @staticmethod
    def get(site_id):
        return PackageSite.query.filter_by(site_id=site_id).first()

    @staticmethod
    def add(site_id, template: PackageTemplate):
        package = PackageSite(
            name=template.name,
            page_views=template.page_views,
            heatmaps=template.heatmaps,
            session_recordings=template.session_recordings,
            ab_testing=template.ab_testing,
            ecommerce=template.ecommerce,
            reports_standard=template.reports_standard,
            reports_power_bi=template.reports_power_bi,
            api_data_download=template.api_data_download,
            api_recommandations=template.api_recommandations,
            api_data_transformation=template.api_data_transformation,
            api_index_search=template.api_index_search,
            api_product_360=template.api_product_360,
            api_custom_searches=template.api_custom_searches,

            price=template.price,
            currency=template.currency,

            on_expiration=template.on_expiration_name,

            site_id=site_id,
            #valid_until=template.validity_period()
            valid_until = template.get_valid_until()
        )

        try:
            db.session.add(package)
            db.session.commit()
        except Exception:
            # TODO add logging and quit gracefully
            db.session.rollback()
            raise

        return package

    @staticmethod
    def update(site_id, template: PackageTemplate):
        attrs = {
            'name': template.name,
            'page_views': template.page_views,
            'heatmaps': template.heatmaps,
            'session_recordings': template.session_recordings,
            'ab_testing': template.ab_testing,
            'ecommerce': template.ecommerce,
            'reports_standard': template.reports_standard,
            'reports_power_bi': template.reports_power_bi,
            'api_data_download': template.api_data_download,
            'api_recommandations': template.api_recommandations,
            'api_data_transformation': template.api_data_transformation,
            'api_index_search': template.api_index_search,
            'api_product_360': template.api_product_360,
            'api_custom_searches': template.api_custom_searches,

            'price': template.price,
            'currency': template.currency,

            'on_expiration': template.on_expiration_name,

            #'valid_until': template.validity_period(),
            'valid_until': template.get_valid_until(),
        }

        try:
            db.session.query(PackageSite).filter(PackageSite.site_id == site_id).update(attrs)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise


def system_update_packages():
    """ Creates new PackagesSite for expired ones """

    items = PackageSite.query.filter_by(replaced_by=None).filter(PackageSite.valid_until <= _now())
    for item in items:
        try:
            template: PackageTemplate = item.on_expiration
            package = PackageSite(
                name=template.name,
                page_views=template.page_views,
                heatmaps=template.heatmaps,
                session_recordings=template.session_recordings,
                ab_testing=template.ab_testing,
                ecommerce=template.ecommerce,
                reports_standard=template.reports_standard,
                reports_power_bi=template.reports_power_bi,
                api_data_download=template.api_data_download,
                api_recommandations=template.api_recommandations,
                api_data_transformation=template.api_data_transformation,
                api_index_search=template.api_index_search,
                api_product_360=template.api_product_360,
                api_custom_searches=template.api_custom_searches,

                price=template.price,
                currency=template.currency,

                on_expiratino=template.on_expiration_name,

                site_id=item.site_id,
                valid_until=template.get_valid_until()
            )

            db.session.add(package)
            db.session.flush()

            item.replace_by = package
            db.session.add(item)
            db.session.commit()
        except Exception:
            # TODO log error
            db.session.rollback()
            raise


def _update_template_from_dict(item: PackageTemplate, row: dict):
    # TODO replace this with a proper deserializer like a Marshmallow Schema

    def _get(field_name, default=None, *, coerce=None):
        value = row[field_name]
        if value == '':
            if default is None:
                return None
            value = default

        return coerce(value) if coerce else value

    item.page_views = _get('page_views', coerce=int)

    item.heatmaps = _get('heatmaps', coerce=int)
    item.session_recordings = _get('session_recordings', coerce=int)
    item.ab_testing = _get('ab_testing', coerce=int)
    item.ecommerce = _get('ecommerce', coerce=lambda x: bool(int(x)))
    item.reports_standard = _get('reports_standard', coerce=int)
    item.reports_power_bi = _get('reports_power_bi', coerce=int)
    item.api_data_download = _get('api_data_download', coerce=int)
    item.api_recommandations = _get('api_recommandations', coerce=int)
    item.api_data_transformation = _get('api_data_transformation', coerce=int)
    item.api_index_search = _get('api_index_search', coerce=int)
    item.api_product_360 = _get('api_product_360', coerce=int)
    item.api_custom_searches = _get('api_custom_searches', coerce=int)

    item.price = _get('price', coerce=Decimal)
    item.currency = _get('currency')

    item.partner_id = _get('partner_id', coerce=int)
    item.validity_period = _get('validity_period', coerce=lambda x: timedelta(days=int(x)))
    item.on_expiration_name = _get('on_expiration', row['name'])
    item.max_sites = _get('max_sites', coerce=int)


@app.cli.command()
@click.option('--path', default=app.config['BASE_DIR'].parent / 'packages.csv')
def sync_packages(path):
    path = Path(path)
    if not path.exists():
        raise click.BadParameter(f'File not found: {path}', param_hint='path')

    templates = {}
    modified = []

    for item in PackageTemplate.query.all():
        templates[item.name] = item

    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['name']
            assert name not in modified, f'Duplicate package with name \'{name}\''

            modified.append(name)

            try:
                obj = templates.pop(name)
            except KeyError:
                obj = PackageTemplate(name=name)

            _update_template_from_dict(obj, row)
            templates[name] = obj

    assert set(templates.keys()).issuperset(set(modified))

    try:
        for deleted in set(templates.keys()) - set(modified):
            db.session.delete(templates[deleted])

        db.session.bulk_save_objects(templates[k] for k in modified)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

