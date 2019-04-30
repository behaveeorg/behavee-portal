import logging
from collections import defaultdict

from flask import request, flash, redirect, abort, url_for
from flask_login import login_required

from app import app, constants
from app.toolbox.matomo import HeatmapSessionRecordingManager, MatomoError, render_template
from app.toolbox.user import get_matomo_user
from app.toolbox.current_site import idsite_required
from app.forms.analytics.heatmaps import HeatmapForm, HeatmapsDeleteForm


def _rules_update_formdata(formdata):
    rules = defaultdict(lambda: {})

    for field_name, field_value in formdata.copy().items():
        if not field_name.startswith('rule'):
            continue

        _, rule_field, rule_index = field_name.split('_', 3)
        rule_index = int(rule_index)

        if rule_field == 'type':
            if field_value.startswith('not_'):
                field_value = field_value.lstrip('not_')
                rules[rule_index]['inverted'] = '1'
            else:
                rules[rule_index]['inverted'] = '0'

        rules[rule_index][rule_field] = field_value.strip()
        del formdata[field_name]

    if rules:
        match_page_rules = []
        for i in sorted(rules):
            # Validate data
            # TODO add form error
            if not rules[i]['value'] or (rules[i]['type'] == 'urlparam' and not rules[i]['value2']):
                continue

            match_page_rules.append(rules[i])

        if match_page_rules:
            formdata['match_page_rules'] = match_page_rules


@app.route('/analytics/heatmaps', methods=['GET'])
@login_required
@idsite_required
def analytics_heatmaps():
    matomo_user = get_matomo_user()

    try:
        idsite = request.args['idSite']
    except KeyError:
        abort(404)  # Fail safe to @site_required

    heatmaps_list = HeatmapSessionRecordingManager().getHeatmaps(matomo_user.token_auth, idsite)

    idsitehsr = request.args.get('idSiteHsr')
    if idsitehsr:
        heatmap = HeatmapSessionRecordingManager().getHeatmap(matomo_user.token_auth, idsite, idsitehsr)
    else:
        return render_template('analytics/heatmaps_list.html', title='Behavee > Analytics > Heatmaps',
                               heatmaps_list=heatmaps_list, idsite=idsite, menuHeatmapsList="active")

    return render_template(
        'analytics/heatmaps.html', title='Behavee > Analytics > Heatmaps', menuHeatmapsList="active", heatmap=heatmap,
        labels={'attribute': dict(constants.RULES), 'type': dict(constants.RULES_TYPE)}
    )


@app.route('/analytics/heatmaps/add', methods=['GET', 'POST'])
@login_required
@idsite_required
def analytics_heatmaps_add():
    form = None
    form_class = HeatmapForm
    idsite = request.args['idSite']

    matomo_user = get_matomo_user()
    count_rules = 1

    if request.method == 'POST':
        try:
            count_rules = int(request.form['count_rules'])
        except KeyError:
            logging.warning(f'No count_rules specified: {repr(request.form)}')
        else:
            form = form_class.with_rules(count_rules, formdata=request.form)

            if form.validate_on_submit():
                data = dict(form.data)
                data['idsite'] = idsite

                _rules_update_formdata(data)

                try:
                    r = HeatmapSessionRecordingManager().addHeatmap(matomo_user.token_auth, **data)
                except MatomoError as e:
                    flash(str(e), 'negative')
                else:
                    if 'value' in r:
                        # return redirect(f"/analytics/heatmaps?idSiteHsr={r['value']}")
                        return redirect(url_for('analytics_heatmaps', idSite=idsite, idSiteHsr=r['value']))

                    # TODO add logging.warning

                return redirect(url_for('analytics_heatmaps', idSite=idsite))

    if form is None:
        form = form_class.with_rules(count_rules)

    return render_template('analytics/heatmaps_add.html', title='Behavee > Analytics > Add Heatmap',
                           heatmap_add_form=form, menuHeatmapsAdd="active", idsite=idsite, count_rules=count_rules)


@app.route('/analytics/heatmaps/<string:idsitehsr>/edit', methods=['GET', 'POST'])
@login_required
@idsite_required
def analytics_heatmaps_edit(idsitehsr):
    form = None
    form_class = HeatmapForm

    idsite = request.args['idSite']
    matomo_user = get_matomo_user()

    if request.method == 'POST':
        try:
            count_rules = int(request.form['count_rules'])
        except KeyError:
            # TODO handle exception
            logging.warning(f'No count_rules specified: {repr(request.form)}')
        else:
            form = form_class.with_rules(count_rules, formdata=request.form)
            if form.validate_on_submit():
                data = dict(form.data)
                data['idsite'] = idsite
                data['idsitehsr'] = idsitehsr

                _rules_update_formdata(data)
                try:
                    HeatmapSessionRecordingManager().updateHeatmap(
                        matomo_user.token_auth, **data
                    )
                except MatomoError as e:
                    flash(str(e), 'negative')
                else:

                    return redirect(url_for('analytics_heatmaps', idSite=idsite, idSiteHsr=idsitehsr), 303)
            else:
                print('FORM_ERRORS', form.errors)

    if form is None:
        try:
            heatmap = HeatmapSessionRecordingManager().getHeatmap(matomo_user.token_auth, idsite, idsitehsr)
        except MatomoError:
            # TODO log error
            abort(404)

        count_rules = len(heatmap['match_page_rules'])

        for i, rule in enumerate(heatmap.pop('match_page_rules')):
            type_ = rule['type']
            if int(rule['inverted']):
                type_ = f'not_{type_}'

            heatmap[f'rules_type_{i}'] = type_
            heatmap[f'rules_attribute_{i}'] = rule['attribute']
            heatmap[f'rules_value_{i}'] = rule['value']
            try:
                heatmap[f'rules_value2_{i}'] = rule['value2']
            except KeyError:
                # We where not supplied with `value2`
                pass

        form = form_class.with_rules(count_rules, **heatmap)

    return render_template('analytics/heatmaps_edit.html', title='Behavee > Analytics > Edit Heatmap',
                           heatmap_edit_form=form, menuHeatmapsList="active", idsite=idsite,
                           idsitehsr=idsitehsr, count_rules=count_rules)


@app.route('/analytics/heatmaps/<string:idsitehsr>/delete', methods=['GET', 'POST'])
@login_required
@idsite_required
def analytics_heatmaps_delete(idsitehsr):
    idsite = request.args['idSite']
    form_class = HeatmapsDeleteForm

    matomo_user = get_matomo_user()
    heatmap = HeatmapSessionRecordingManager().getHeatmap(matomo_user.token_auth, idsite, idsitehsr)

    if request.method == 'POST':
        form = form_class(formdata=request.form)
        if form.validate_on_submit():
            name = form.data['name'].strip()

            if heatmap['name'].strip() == name:
                try:
                    HeatmapSessionRecordingManager().deleteHeatmap(matomo_user.token_auth, idsite, idsitehsr)
                except MatomoError as e:
                    flash(str(e), 'negative')
                else:
                    flash(f"Heatmap '{heatmap['name']}' was deleted")
                    return redirect(url_for('analytics_heatmaps', idSite=idsite))
            else:
                flash('Name does not match', 'negative')

    form = form_class()

    return render_template('analytics/heatmaps_delete.html', title='Behavee > Analytics > Delete Heatmap',
                           heatmaps_delete_form=form, menuHeatmapsList="active", idsite=idsite,
                           idsitehsr=idsitehsr, heatmap=heatmap)

@app.route('/analytics/heatmaps/<string:idsitehsr>/show', methods=['GET'])
@login_required
@idsite_required
def analytics_heatmaps_show(idsitehsr):
    idsite = request.args['idSite']
    matomo_user = get_matomo_user()

    # try:
    #     heatmap = HeatmapSessionRecordingManager().getHeatmap(matomo_user.token_auth, idsite, idsitehsr)
    # except MatomoError:
    #     # TODO log error
    #     abort(404)

    return render_template('analytics/heatmaps_show.html', title='Behavee > Analytics > Show Heatmap',app=app,
                           menuHeatmapsList="active", idsite=idsite,
                           idsitehsr=idsitehsr)
