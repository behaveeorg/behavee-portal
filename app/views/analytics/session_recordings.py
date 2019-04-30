import logging

from flask import request, abort, render_template, flash, redirect, url_for
from flask_login import login_required

from app import app, constants
from app.forms.analytics.session_recordings import SessionRecordingForm, SessionRecordingDeleteForm
from app.toolbox.matomo import HeatmapSessionRecordingManager, MatomoError
from app.toolbox.user import get_matomo_user
from app.toolbox.current_site import idsite_required
from app.views.analytics.heatmaps import _rules_update_formdata


@app.route('/analytics/session-recordings', methods=['GET'])
@login_required
@idsite_required
def analytics_session_recordings():

    matomo_user = get_matomo_user()

    try:
        idsite = request.args['idSite']
    except KeyError:
        abort(404)  # Fail safe to @site_required

    idsitehsr = request.args.get('idSiteHsr')
    if idsitehsr:
        recording = HeatmapSessionRecordingManager().getSessionRecording(matomo_user.token_auth, idsite, idsitehsr)
    else:
        recordings_list = HeatmapSessionRecordingManager().getSessionRecordings(matomo_user.token_auth, idsite)
        return render_template(
            'analytics/session_recordings_list.html', title='Behavee > Analytics > Session Recordings',
            recordings_list=recordings_list, idsite=idsite, menuSessionRecordingsList="active"
        )

    return render_template(
        'analytics/session_recordings.html', title='Behavee > Analytics > Session Recordings',
        menuSessionRecordingsList="active", recording=recording,
        labels={'attribute': dict(constants.RULES), 'type': dict(constants.RULES_TYPE)}
    )


@app.route('/analytics/session-recordings/add', methods=['GET', 'POST'])
@login_required
@idsite_required
def analytics_session_recordings_add():
    form = None
    form_class = SessionRecordingForm

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
                    r = HeatmapSessionRecordingManager().addSessionRecording(matomo_user.token_auth, **data)
                except MatomoError as e:
                    flash(str(e), 'negative')
                    print('ERRORS', str(e))
                else:
                    if 'value' in r:
                        # return redirect(f"/analytics/heatmaps?idSiteHsr={r['value']}")
                        return redirect(url_for('analytics_session_recordings', idSite=idsite, idSiteHsr=r['value']))

                return redirect(url_for('analytics_session_recordings', idSite=idsite))

            else:
                print('FORM ERRORS', form.errors)

    if form is None:
        form = form_class.with_rules(count_rules)

    return render_template('analytics/session_recordings_add.html', title='Behavee > Analytics > Add Session Recording',
                           recording_add_form=form, menuSessionRecordingsAdd="active",
                           count_rules=count_rules, idsite=idsite)


@app.route('/analytics/session-recordings/<string:idsitehsr>/edit', methods=['GET', 'POST'])
@login_required
@idsite_required
def analytics_session_recordings_edit(idsitehsr):
    form = None
    form_class = SessionRecordingForm

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
                    HeatmapSessionRecordingManager().updateSessionRecording(matomo_user.token_auth, **data)
                except MatomoError as e:
                    flash(str(e), 'negative')
                    print('ERROR', e.response)
                else:
                    print('what')
                    return redirect(url_for('analytics_session_recordings', idSite=idsite, idSiteHsr=idsitehsr), 303)
            else:
                print('FORM_ERRORS', form.errors)

    if form is None:
        try:
            recording = HeatmapSessionRecordingManager().getSessionRecording(matomo_user.token_auth, idsite, idsitehsr)
        except MatomoError:
            # TODO log error
            abort(404)

        count_rules = len(recording['match_page_rules'])

        for i, rule in enumerate(recording.pop('match_page_rules')):
            type_ = rule['type']
            if int(rule['inverted']):
                type_ = f'not_{type_}'

            recording[f'rules_type_{i}'] = type_
            recording[f'rules_attribute_{i}'] = rule['attribute']
            recording[f'rules_value_{i}'] = rule['value']
            try:
                recording[f'rules_value2_{i}'] = rule['value2']
            except KeyError:
                # We where not supplied with `value2`
                pass


        form = form_class.with_rules(count_rules, **recording)

    return render_template('analytics/session_recordings_edit.html',
                           title='Behavee > Analytics > Edit Session Recording', recording_edit_form=form,
                           menuSessionRecordingsList="active", idsite=idsite,
                           idsitehsr=idsitehsr, count_rules=count_rules)


@app.route('/analytics/session-recordings/<string:idsitehsr>/delete', methods=['GET', 'POST'])
@login_required
@idsite_required
def analytics_session_recordings_delete(idsitehsr):
    idsite = request.args['idSite']
    form_class = SessionRecordingDeleteForm

    matomo_user = get_matomo_user()
    recording = HeatmapSessionRecordingManager().getSessionRecording(matomo_user.token_auth, idsite, idsitehsr)

    if request.method == 'POST':
        form = form_class(formdata=request.form)
        if form.validate_on_submit():
            name = form.data['name'].strip()

            if recording['name'] == name:
                try:
                    HeatmapSessionRecordingManager().deleteSessionRecording(matomo_user.token_auth, idsite, idsitehsr)
                except MatomoError as e:
                    flash(str(e), 'negative')
                else:
                    flash(f"Session recording '{recording['name']}' was deleted")
                    return redirect(url_for('analytics_session_recordings', idSite=idsite))
            else:
                flash('Name does not match', 'negative')

    form = form_class()

    return render_template('analytics/session_recordings_delete.html',
                           title='Behavee > Analytics > Delete Session Recording',
                           recording_delete_form=form, menuSessionRecordingsList="active", idsite=idsite,
                           idsitehsr=idsitehsr, recording=recording)

@app.route('/analytics/session-recordings/<string:idsitehsr>/show', methods=['GET'])
@login_required
@idsite_required
def analytics_session_recordings_show(idsitehsr):
    form = None
    form_class = SessionRecordingForm

    idsite = request.args['idSite']
    matomo_user = get_matomo_user()


    if form is None:
        try:
            recording = HeatmapSessionRecordingManager().getSessionRecording(matomo_user.token_auth, idsite, idsitehsr)
        except MatomoError:
            # TODO log error
            abort(404)

        count_rules = len(recording['match_page_rules'])

        for i, rule in enumerate(recording.pop('match_page_rules')):
            type_ = rule['type']
            if int(rule['inverted']):
                type_ = f'not_{type_}'

            recording[f'rules_type_{i}'] = type_
            recording[f'rules_attribute_{i}'] = rule['attribute']
            recording[f'rules_value_{i}'] = rule['value']
            try:
                recording[f'rules_value2_{i}'] = rule['value2']
            except KeyError:
                # We where not supplied with `value2`
                pass


        form = form_class.with_rules(count_rules, **recording)

    return render_template('analytics/session_recordings_show.html',
                           title='Behavee > Analytics > Show Session Recording',app=app, recording_edit_form=form,
                           menuSessionRecordingsList="active", idsite=idsite,
                           idsitehsr=idsitehsr, count_rules=count_rules)
