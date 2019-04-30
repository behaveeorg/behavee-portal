from flask import render_template, request, redirect, url_for

from app import app, login_required
from app.forms.partner import PartnerForm
from app.models.behavee import PartnerUserRelManager
from app.toolbox.user import get_matomo_user


@app.route('/account/partner/profile', methods=['GET', 'POST'])
@login_required
def partner_profile_view():
    user = get_matomo_user()

    partner = PartnerUserRelManager.get_partner(user.login)

    if partner:
        return render_template(
            'account/partner_view.html', title='Behavee > Account > Partner',
            partner=partner, menuSettingsPartner="active",
        )
    else:
        form_class = PartnerForm
        form = form_class()
        return render_template(
            'account/partner_edit.html', title='Behavee > Account > Partner',
            partner_form=form, menuSettingsPartner="active",
        )

@app.route('/account/partner/', methods=['GET', 'POST'])
@login_required
def partner_edit_view():
    user = get_matomo_user()
    form_class = PartnerForm

    partner = PartnerUserRelManager.get_partner(user.login)

    if request.method == 'POST':
        form = form_class(request.form)
        data = form.data

        if partner:
            PartnerUserRelManager.update(matomo_user_id=user.login, **data)
            return redirect(url_for('partner_profile_view'), 303)
        else:
            PartnerUserRelManager.add(matomo_user_id=user.login, **data)
            return redirect(url_for('partner_profile_view'), 303)

    if partner:
        if len(partner.geo_location) > 0:
            form = form_class(
                name=partner.name,
                description=partner.description,
                company_number=partner.company_number,
                vat_number=partner.vat_number,
                partner_type=partner.partner_type,
                address_city = partner.geo_location[0].city,
                address_street = partner.geo_location[0].street,
                address_street_no = partner.geo_location[0].street_no,
                address_zip_code = partner.geo_location[0].zip_code,
                address_longitude = partner.geo_location[0].longitude,
                address_latitude = partner.geo_location[0].latitude,
                address_country_code = partner.geo_location[0].country_code,
                address_geo_location_type = partner.geo_location[0].geo_location_type,
        )
        else:
            form = form_class(
                name=partner.name,
                description=partner.description,
                company_number=partner.company_number,
                vat_number=partner.vat_number,
                partner_type=partner.partner_type,
                address_city=None,
                address_street=None,
                address_street_no=None,
                address_zip_code=None,
                address_longitude=None,
                address_latitude=None,
                address_country_code=None,
                address_geo_location_type=None,
            )
    else:
        form = form_class()

    return render_template(
        'account/partner_edit.html', title='Behavee > Account > Partner',
        partner_form=form, menuSettingsPartner="active",
    )