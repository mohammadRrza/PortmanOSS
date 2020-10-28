from django.shortcuts import render
from django.template import RequestContext
from datetime import date, timedelta
from django.db.models import Count
from dslam.models import DSLAM, DSLAMPort, DSLAMPortSnapshot
import simplejson as json


######## Custom Views

def view_dslam_report(request, *args, **kwargs):
    dslam_id = int(request.GET.get('dslam_id'))
    dslam_obj = DSLAM.objects.get(id=dslam_id)

    queryset = DSLAMPort.objects.filter(dslam=dslam_obj)
    total_ports = queryset.count()
    up_ports = queryset.filter(admin_status='UNLOCK').count()
    down_ports = queryset.filter(admin_status='LOCK').count()
    sync_ports = queryset.filter(oper_status='SYNC').count()
    nosync_ports = queryset.filter(oper_status='NO-SYNC').count()

    line_profile_usage = DSLAMPort.objects.values(
        'line_profile'
    ).filter(dslam=dslam_obj).annotate(
        usage_count=Count('line_profile')
    )

    line_profile_usage = [{'name':str(item['line_profile']), 'y':item['usage_count']} for item in line_profile_usage]

    return render_to_response(
            'dslam_report.html',
            {'dslam':dslam_obj, 'total_ports':total_ports,
             'up_ports':up_ports, 'down_ports':down_ports, 'sync_ports':sync_ports,
             'nosync_ports':nosync_ports, 'line_profile_usage':json.dumps(line_profile_usage)}
          )
                #context_instance = RequestContext(request))




def view_port_status_report(request, *args, **kwargs):
    dslam_id = int(request.GET.get('dslam_id'))
    port_id = int(request.GET.get('port_id'))

    dslam_obj = DSLAM.objects.get(id=dslam_id)
    port_obj = DSLAMPort.objects.get(id=port_id)

    snp_date_from = date.today() - timedelta(hours=72)
    port_snapshots = DSLAMPortSnapshot.objects.filter(
        dslam_id=dslam_id
    ).filter(
        port_index=port_obj.port_index
    ).filter(snp_date__gte=snp_date_from).order_by('snp_date')

    up_snr_data, down_snr_data = [], []
    up_tx_rate, down_tx_rate = [], []
    up_attenuation, down_attenuation = [], []
    up_attainable_rate, down_attainable_rate = [], []

    oper_status = {'SYNC':0, 'NO-SYNC':0, 'OTHER':0}#up_count, down_count
    dates = []
    for snp in port_snapshots:
        dates.append(snp.snp_date.strftime('%Y-%m-%d %H:%M'))
        if snp.oper_status in ['SYNC', 'NO-SYNC']:
            oper_status[snp.oper_status]+=1
        else:
            oper_status['OTHER'] += 1

        up_snr_data.append(snp.upstream_snr)
        down_snr_data.append(snp.downstream_snr)
        up_tx_rate.append(snp.upstream_tx_rate)
        down_tx_rate.append(snp.downstream_tx_rate)
        up_attenuation.append(snp.upstream_attenuation)
        down_attenuation.append(snp.downstream_attenuation)
        up_attainable_rate.append(snp.upstream_attainable_rate)
        down_attainable_rate.append(snp.downstream_attainable_rate)

    snr_data = [{'name':'UP Stream SNR', 'data':up_snr_data}, {'name':'DOWN Stream SNR', 'data':down_snr_data}]
    attenuation_data = [{'name':'UP Stream Attenuation', 'data':up_attenuation},
                        {'name':'DOWN Stream Attenuation', 'data':down_attenuation}]
    tx_data = [{'name':'Down Stream TX Rate', 'data':down_tx_rate}, {'name':'UP Stream TX Rate', 'data':up_tx_rate}]
    attainable_rate_data = [{'name':'UP Stream Attainable Rate', 'data':up_attainable_rate},
                            {'name':'DOWN Stream Attainable Rate', 'data':down_attainable_rate}]
    oper_status_data = [{'name':name, 'y':value} for name,value in oper_status.iteritems()]

    return render_to_response(
            'port_status_report.html',
            {'dslam':dslam_obj, 'port':port_obj,
             'dates':json.dumps(dates),
             'oper_status':json.dumps(oper_status_data),
             'snr_data':json.dumps(snr_data),
             'attenuation_data':json.dumps(attenuation_data),
             'tx_data':json.dumps(tx_data),
             'attainable_rate_data':json.dumps(attainable_rate_data)
            })


