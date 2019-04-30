#!/usr/bin/env python3
import requests, json
from flask import render_template, flash, redirect
from app import app, db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import BigInteger, DateTime, Date, Time, Text, Binary, \
    SmallInteger, Float, DECIMAL as Decimal, Integer, String, ForeignKey
from flask_security import current_user
from urllib.parse import urlencode, quote_plus
from requests.auth import HTTPBasicAuth
from werkzeug.exceptions import BadRequest
import urllib.parse
#import secrets
from app.toolbox.matomo import MatomoAnalytics


class Access(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    login = db.Column(String(100))
    idsite = db.Column(Integer())
    access = db.Column(String(10))

    class Meta:
        managed = False
        db_table = 'access'
        unique_together = (('login', 'idsite'),)
        verbose_name_plural = db_table


# class ArchiveBlob200812(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2008_12'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201701(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_01'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201706(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_06'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201707(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_07'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201708(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_08'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201709(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_09'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201710(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_10'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveBlob201711(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Text())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_blob_2017_11'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric200812(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2008_12'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201701(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_01'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201706(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_06'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201707(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_07'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201708(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_08'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201709(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_09'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201710(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_10'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table
#
#
# class ArchiveNumeric201711(db.Model):
#     __bind_key__ = 'matomo'
#     idarchive = db.Column(Integer())
#     name = db.Column(String(255))
#     idsite = db.Column(Integer())
#     date1 = db.Column(Date())
#     date2 = db.Column(Date())
#     period = db.Column(Integer())
#     ts_archived = db.Column(DateTime())
#     value = db.Column(Float())
#
#     class Meta:
#         managed = False
#         db_table = 'archive_numeric_2017_11'
#         unique_together = (('idarchive', 'name'),)
#         verbose_name_plural = db_table


class BotDb(db.Model):
    __bind_key__ = 'matomo'
    botid = db.Column(Integer(), primary_key=True)  # Field name made lowercase.
    idsite = db.Column(Integer())
    botname = db.Column(String(100))  # Field name made lowercase.
    botactive = db.Column(Integer())  # Field name made lowercase.
    botkeyword = db.Column(String(32))  # Field name made lowercase.
    botcount = db.Column(Integer())  # Field name made lowercase.
    botlastvisit = db.Column(DateTime())  # Field name made lowercase.
    extra_stats = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'bot_db'
        verbose_name_plural = db_table


class BotDbStat(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    botid = db.Column(Integer())  # Field name made lowercase.
    idsite = db.Column(Integer())
    page = db.Column(String(100))
    visit_timestamp = db.Column(DateTime())
    useragent = db.Column(String(100))

    class Meta:
        managed = False
        db_table = 'bot_db_stat'
        unique_together = (('botid', 'visit_timestamp'),)
        verbose_name_plural = db_table


class Goal(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    idgoal = db.Column(Integer())
    name = db.Column(String(50))
    description = db.Column(String(255))
    match_attribute = db.Column(String(20))
    pattern = db.Column(String(255))
    pattern_type = db.Column(String(10))
    case_sensitive = db.Column(Integer())
    allow_multiple = db.Column(Integer())
    revenue = db.Column(Float())
    deleted = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'goal'
        unique_together = (('idsite', 'idgoal'),)
        verbose_name_plural = db_table


class HmiProducts(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    id_sku = db.Column(Integer())
    name = db.Column(String(36))
    short_description = db.Column(String(35))
    weight = db.Column(Float())
    length = db.Column(Float())
    width = db.Column(Float())
    height = db.Column(Float())
    sale_price = db.Column(Float())
    regular_price = db.Column(Float())
    categories = db.Column(String(28))
    tags = db.Column(String(2))
    images = db.Column(String(206))
    parent = db.Column(String(10))

    class Meta:
        managed = False
        db_table = 'hmi_products'
        verbose_name_plural = db_table


class LogAction(db.Model):
    __bind_key__ = 'matomo'
    idaction = db.Column(Integer(), primary_key=True)
    name = db.Column(Text())
    hash = db.Column(Integer())
    type = db.Column(Integer())
    url_prefix = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'log_action'
        verbose_name_plural = db_table


class LogConversion(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    idvisit = db.Column(BigInteger())
    idsite = db.Column(Integer())
    idvisitor = db.Column(Binary())
    server_time = db.Column(DateTime(), primary_key=True)
    idaction_url = db.Column(Integer())
    idlink_va = db.Column(BigInteger())
    idgoal = db.Column(Integer())
    buster = db.Column(Integer())
    idorder = db.Column(String(100))
    items = db.Column(SmallInteger())
    url = db.Column(Text())
    visitor_days_since_first = db.Column(SmallInteger())
    visitor_days_since_order = db.Column(SmallInteger())
    visitor_returning = db.Column(Integer())
    visitor_count_visits = db.Column(Integer())
    referer_keyword = db.Column(String(255))
    referer_name = db.Column(String(70))
    referer_type = db.Column(Integer())
    config_device_brand = db.Column(String(100))
    config_device_model = db.Column(String(100))
    config_device_type = db.Column(Integer())
    location_city = db.Column(String(255))
    location_country = db.Column(String(3))
    location_latitude = db.Column(Decimal(9, 6))
    location_longitude = db.Column(Decimal(9, 6))
    location_region = db.Column(String(2))
    revenue = db.Column(Float())
    revenue_discount = db.Column(Float())
    revenue_shipping = db.Column(Float())
    revenue_subtotal = db.Column(Float())
    revenue_tax = db.Column(Float())
    custom_var_k1 = db.Column(String(200))
    custom_var_v1 = db.Column(String(200))
    custom_var_k2 = db.Column(String(200))
    custom_var_v2 = db.Column(String(200))
    custom_var_k3 = db.Column(String(200))
    custom_var_v3 = db.Column(String(200))
    custom_var_k4 = db.Column(String(200))
    custom_var_v4 = db.Column(String(200))
    custom_var_k5 = db.Column(String(200))
    custom_var_v5 = db.Column(String(200))
    example_conversion_dimension = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'log_conversion'
        unique_together = (('idvisit', 'idgoal', 'buster'), ('idsite', 'idorder'),)
        verbose_name_plural = db_table


class LogConversionItem(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    idvisitor = db.Column(String(8))
    server_time = db.Column(DateTime(), primary_key=True)
    idvisit = db.Column(BigInteger())
    idorder = db.Column(String(100))
    idaction_sku = db.Column(Integer())
    idaction_name = db.Column(Integer())
    idaction_category = db.Column(Integer())
    idaction_category2 = db.Column(Integer())
    idaction_category3 = db.Column(Integer())
    idaction_category4 = db.Column(Integer())
    idaction_category5 = db.Column(Integer())
    price = db.Column(Float())
    quantity = db.Column(Integer())
    deleted = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'log_conversion_item'
        unique_together = (('idvisit', 'idorder', 'idaction_sku'),)
        verbose_name_plural = db_table


class LogLinkVisitAction(db.Model):
    __bind_key__ = 'matomo'
    idlink_va = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    idvisitor = db.Column(String(8))
    idvisit = db.Column(BigInteger())
    idaction_url_ref = db.Column(Integer())
    idaction_name_ref = db.Column(Integer())
    custom_float = db.Column(Float())
    server_time = db.Column(DateTime())
    idpageview = db.Column(String(6))
    interaction_position = db.Column(SmallInteger())
    idaction_name = db.Column(Integer())
    idaction_url = db.Column(Integer())
    time_spent_ref_action = db.Column(Integer())
    idaction_event_action = db.Column(Integer())
    idaction_event_category = db.Column(Integer())
    idaction_content_interaction = db.Column(Integer())
    idaction_content_name = db.Column(Integer())
    idaction_content_piece = db.Column(Integer())
    idaction_content_target = db.Column(Integer())
    custom_var_k1 = db.Column(String(200))
    custom_var_v1 = db.Column(String(200))
    custom_var_k2 = db.Column(String(200))
    custom_var_v2 = db.Column(String(200))
    custom_var_k3 = db.Column(String(200))
    custom_var_v3 = db.Column(String(200))
    custom_var_k4 = db.Column(String(200))
    custom_var_v4 = db.Column(String(200))
    custom_var_k5 = db.Column(String(200))
    custom_var_v5 = db.Column(String(200))
    bandwidth = db.Column(BigInteger())
    example_action_dimension = db.Column(String(255))

    class Meta:
        managed = False
        db_table = 'log_link_visit_action'
        verbose_name_plural = db_table


class LogProfiling(db.Model):
    __bind_key__ = 'matomo'

    id = db.Column(BigInteger(), primary_key=True)
    query = db.Column(Text(), unique=True)
    count = db.Column(Integer())
    sum_time_ms = db.Column(Float())

    class Meta:
        managed = False
        db_table = 'log_profiling'
        verbose_name_plural = db_table


class LogVisit(db.Model):
    __bind_key__ = 'matomo'

    idvisit = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    idvisitor = db.Column(Binary())
    visit_last_action_time = db.Column(DateTime())
    config_id = db.Column(Binary())
    location_ip = db.Column(Binary())
    user_id = db.Column(String(200))
    visit_first_action_time = db.Column(DateTime())
    visit_goal_buyer = db.Column(Integer())
    visit_goal_converted = db.Column(Integer())
    visitor_days_since_first = db.Column(SmallInteger())
    visitor_days_since_order = db.Column(SmallInteger())
    visitor_returning = db.Column(Integer())
    visitor_count_visits = db.Column(Integer())
    visit_entry_idaction_name = db.Column(Integer())
    visit_entry_idaction_url = db.Column(Integer())
    visit_exit_idaction_name = db.Column(Integer())
    visit_exit_idaction_url = db.Column(Integer())
    visit_total_actions = db.Column(Integer())
    visit_total_interactions = db.Column(SmallInteger())
    visit_total_searches = db.Column(SmallInteger())
    referer_keyword = db.Column(String(255))
    referer_name = db.Column(String(70))
    referer_type = db.Column(Integer())
    referer_url = db.Column(Text())
    location_browser_lang = db.Column(String(20))
    config_browser_engine = db.Column(String(10))
    config_browser_name = db.Column(String(10))
    config_browser_version = db.Column(String(20))
    config_device_brand = db.Column(String(100))
    config_device_model = db.Column(String(100))
    config_device_type = db.Column(Integer())
    config_os = db.Column(String(3))
    config_os_version = db.Column(String(100))
    visit_total_events = db.Column(Integer())
    visitor_localtime = db.Column(Time())
    visitor_days_since_last = db.Column(SmallInteger())
    config_resolution = db.Column(String(18))
    config_cookie = db.Column(Integer())
    config_director = db.Column(Integer())
    config_flash = db.Column(Integer())
    config_gears = db.Column(Integer())
    config_java = db.Column(Integer())
    config_pdf = db.Column(Integer())
    config_quicktime = db.Column(Integer())
    config_realplayer = db.Column(Integer())
    config_silverlight = db.Column(Integer())
    config_windowsmedia = db.Column(Integer())
    visit_total_time = db.Column(Integer())
    location_city = db.Column(String(255))
    location_country = db.Column(String(3))
    location_latitude = db.Column(Decimal(9, 6))
    location_longitude = db.Column(Decimal(9, 6))
    location_region = db.Column(String(2))
    custom_var_k1 = db.Column(String(200))
    custom_var_v1 = db.Column(String(200))
    custom_var_k2 = db.Column(String(200))
    custom_var_v2 = db.Column(String(200))
    custom_var_k3 = db.Column(String(200))
    custom_var_v3 = db.Column(String(200))
    custom_var_k4 = db.Column(String(200))
    custom_var_v4 = db.Column(String(200))
    custom_var_k5 = db.Column(String(200))
    custom_var_v5 = db.Column(String(200))
    location_provider = db.Column(String(200))
    location_hostname = db.Column(String(255))
    example_visit_dimension = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'log_visit'
        verbose_name_plural = db_table


class LoggerMessage(db.Model):
    __bind_key__ = 'matomo'
    idlogger_message = db.Column(Integer(), primary_key=True)
    tag = db.Column(String(50))
    timestamp = db.Column(DateTime())
    level = db.Column(String(16))
    message = db.Column(Text())

    class Meta:
        managed = False
        db_table = 'logger_message'
        verbose_name_plural = db_table


class Option(db.Model):
    __bind_key__ = 'matomo'
    option_name = db.Column(String(255), primary_key=True)
    option_value = db.Column(Text())
    autoload = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'option'
        verbose_name_plural = db_table


class PluginSetting(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    plugin_name = db.Column(String(60))
    setting_name = db.Column(String(255))
    setting_value = db.Column(Text())
    user_login = db.Column(String(100))

    class Meta:
        managed = False
        db_table = 'plugin_setting'
        verbose_name_plural = db_table


class Report(db.Model):
    __bind_key__ = 'matomo'
    idreport = db.Column(Integer(), primary_key=True)
    idsite = db.Column(Integer())
    login = db.Column(String(100))
    description = db.Column(String(255))
    idsegment = db.Column(Integer())
    period = db.Column(String(10))
    hour = db.Column(Integer())
    type = db.Column(String(10))
    format = db.Column(String(10))
    reports = db.Column(Text())
    parameters = db.Column(Text())
    ts_created = db.Column(DateTime())
    ts_last_sent = db.Column(DateTime())
    deleted = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'report'
        verbose_name_plural = db_table


class Segment(db.Model):
    __bind_key__ = 'matomo'
    idsegment = db.Column(Integer(), primary_key=True)
    name = db.Column(String(255))
    definition = db.Column(Text())
    login = db.Column(String(100))
    enable_all_users = db.Column(Integer())
    enable_only_idsite = db.Column(Integer())
    auto_archive = db.Column(Integer())
    ts_created = db.Column(DateTime())
    ts_last_edit = db.Column(DateTime())
    deleted = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'segment'
        verbose_name_plural = db_table


class Sequence(db.Model):
    __bind_key__ = 'matomo'
    name = db.Column(String(120), primary_key=True)
    value = db.Column(BigInteger())

    class Meta:
        managed = False
        db_table = 'sequence'
        verbose_name_plural = db_table


class Session(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(String(255), primary_key=True)
    modified = db.Column(Integer())
    lifetime = db.Column(Integer())
    data = db.Column(Text())

    class Meta:
        managed = False
        db_table = 'session'
        verbose_name_plural = db_table


class Site(db.Model):
    __bind_key__ = 'matomo'

    idsite = db.Column(Integer(), primary_key=True)
    name = db.Column(String(90))
    main_url = db.Column(String(255))
    ts_created = db.Column(DateTime())
    ecommerce = db.Column(Integer())
    sitesearch = db.Column(Integer())
    sitesearch_keyword_parameters = db.Column(Text())
    sitesearch_category_parameters = db.Column(Text())
    timezone = db.Column(String(50))
    currency = db.Column(String(3))
    exclude_unknown_urls = db.Column(Integer())
    excluded_ips = db.Column(Text())
    excluded_parameters = db.Column(Text())
    excluded_user_agents = db.Column(Text())
    group = db.Column(String(250))
    type = db.Column(String(255))
    keep_url_fragment = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'site'
        verbose_name_plural = db_table


class SiteSetting(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    plugin_name = db.Column(String(60))
    setting_name = db.Column(String(255))
    setting_value = db.Column(Text())

    class Meta:
        managed = False
        db_table = 'site_setting'
        verbose_name_plural = db_table


class SiteUrl(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    idsite = db.Column(Integer())
    url = db.Column(String(255))

    class Meta:
        managed = False
        db_table = 'site_url'
        unique_together = (('idsite', 'url'),)
        verbose_name_plural = db_table


class MatomoUser(db.Model):
    __bind_key__ = 'matomo'
    __tablename__ = 'user'

    login = db.Column(String(100), primary_key=True)
    password = db.Column(String(255))
    alias = db.Column(String(45))
    email = db.Column(String(100), unique=True)
    token_auth = db.Column(String(32), unique=True)
    superuser_access = db.Column(Integer())
    date_registered = db.Column(DateTime())

    class Meta:
        managed = False

    def __str__(self):
        return self.email

    def __hash__(self):
        return hash(self.email)


class UserDashboard(db.Model):
    __bind_key__ = 'matomo'
    id = db.Column(BigInteger(), primary_key=True)
    login = db.Column(String(100))
    iddashboard = db.Column(Integer())
    name = db.Column(String(100))
    layout = db.Column(Text())

    class Meta:
        managed = False
        db_table = 'user_dashboard'
        unique_together = (('login', 'iddashboard'),)
        verbose_name_plural = db_table


class UserLanguage(db.Model):
    __bind_key__ = 'matomo'
    login = db.Column(String(100), primary_key=True)
    language = db.Column(String(10))
    use_12_hour_clock = db.Column(Integer())

    class Meta:
        managed = False
        db_table = 'user_language'
        verbose_name_plural = db_table
