# Generated by Django 4.2.10 on 2024-03-14 18:30

from django.db import migrations

from olympia import amo

@amo.decorators.use_primary_db
def backfill_cinder_decisions_from_cinder_jobs(apps, schema_editor):
    def get_initial_abuse_report(job):
        return job.abusereport_set.first() or (
            (appealled_job := job.appealed_jobs.first())
            and get_initial_abuse_report(appealled_job)
        )

    CinderJob = apps.get_model('abuse', 'CinderJob')
    CinderDecision = apps.get_model('abuse', 'CinderDecision')
    Addon = apps.get_model('addons', 'Addon')
    cinder_jobs = {}
    decisions_to_create = []
    policies_per_job = {}
    qs = CinderJob.objects.exclude(decision_action=0).exclude(decision_cinder_id='').prefetch_related('policies')
    # generate the list of CinderDecision instances to create
    for cinder_job in qs:
        abuse_report = get_initial_abuse_report(cinder_job)
        if not abuse_report:
            continue
        if abuse_report.guid:
            addon = cinder_job.target_addon or Addon.unfiltered.filter(guid=abuse_report.guid).first()
            if not addon:
                continue
        else:
            addon = None
        decision = CinderDecision(
            action=cinder_job.decision_action,
            cinder_id=cinder_job.decision_cinder_id,
            date=cinder_job.decision_date,
            notes=cinder_job.decision_notes,
            appeal_job=cinder_job.appeal_job,
            addon=addon,
            user=abuse_report.user,
            rating=abuse_report.rating,
            collection=abuse_report.collection,
        )
        decisions_to_create.append(decision)
        # also track the new m2m relationships we'll need the policies, and the back links to the job
        policies_per_job[cinder_job.decision_cinder_id] = list(cinder_job.policies.all())
        cinder_jobs[cinder_job.decision_cinder_id] = cinder_job

    # Bulk create the CinderDecisions
    CinderDecision.objects.bulk_create(decisions_to_create, ignore_conflicts=True)

    m2m_policies_to_create = []
    # Loop through the CinderDecisions, to generate the m2m list and to set cinderjob.decision
    for decision in CinderDecision.objects.all():
        if decision.cinder_id in policies_per_job:
            m2m_policies_to_create.extend(
                CinderDecision.policies.through(cinderdecision=decision, cinderpolicy=policy)
                for policy in policies_per_job[decision.cinder_id]
            )
        if decision.cinder_id in cinder_jobs:
            cinder_jobs[decision.cinder_id].decision = decision

    # Bulk create the CinderDecision<->CinderPolicy relationships
    CinderDecision.policies.through.objects.bulk_create(m2m_policies_to_create, ignore_conflicts=True)
    # And finally bulk update the CinderJobs
    CinderJob.objects.bulk_update(cinder_jobs.values(), ['decision'])


def delete_cinder_decisions(apps, schema_editor):
    CinderDecision = apps.get_model('abuse', 'CinderDecision')
    CinderDecision.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('abuse', '0027_add_cinderdecision'),
    ]

    operations = [
        migrations.RunPython(backfill_cinder_decisions_from_cinder_jobs, delete_cinder_decisions)
    ]
