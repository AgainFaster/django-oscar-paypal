# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ExpressTransaction'
        db.create_table('paypal_expresstransaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_request', self.gf('django.db.models.fields.TextField')(max_length=512)),
            ('raw_response', self.gf('django.db.models.fields.TextField')(max_length=512)),
            ('response_time', self.gf('django.db.models.fields.FloatField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('ack', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('correlation_id', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('error_code', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('error_message', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('paypal', ['ExpressTransaction'])

        # Adding model 'PayflowTransaction'
        db.create_table('paypal_payflowtransaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('raw_request', self.gf('django.db.models.fields.TextField')(max_length=512)),
            ('raw_response', self.gf('django.db.models.fields.TextField')(max_length=512)),
            ('response_time', self.gf('django.db.models.fields.FloatField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('comment1', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('trxtype', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('tender', self.gf('django.db.models.fields.CharField')(max_length=12, null=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('pnref', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('ppref', self.gf('django.db.models.fields.CharField')(max_length=32, unique=True, null=True)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('respmsg', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('authcode', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('cvv2match', self.gf('django.db.models.fields.CharField')(max_length=12, null=True, blank=True)),
            ('avsaddr', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('avszip', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
        ))
        db.send_create_signal('paypal', ['PayflowTransaction'])


    def backwards(self, orm):
        # Deleting model 'ExpressTransaction'
        db.delete_table('paypal_expresstransaction')

        # Deleting model 'PayflowTransaction'
        db.delete_table('paypal_payflowtransaction')


    models = {
        'paypal.expresstransaction': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'ExpressTransaction'},
            'ack': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'correlation_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'error_message': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'raw_request': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'raw_response': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'response_time': ('django.db.models.fields.FloatField', [], {}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '8'})
        },
        'paypal.payflowtransaction': {
            'Meta': {'ordering': "('-date_created',)", 'object_name': 'PayflowTransaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'authcode': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'avsaddr': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'avszip': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'comment1': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'cvv2match': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pnref': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'ppref': ('django.db.models.fields.CharField', [], {'max_length': '32', 'unique': 'True', 'null': 'True'}),
            'raw_request': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'raw_response': ('django.db.models.fields.TextField', [], {'max_length': '512'}),
            'respmsg': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'response_time': ('django.db.models.fields.FloatField', [], {}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'tender': ('django.db.models.fields.CharField', [], {'max_length': '12', 'null': 'True'}),
            'trxtype': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        }
    }

    complete_apps = ['paypal']