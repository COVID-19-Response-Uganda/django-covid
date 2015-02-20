def modify(settings):
    
    settings['INSTALLED_APPS'] += ('crispy_forms', 'tastypie', 'tinymce', 'django_wysiwyg', 'haystack', 'sorl.thumbnail')
    settings['MIDDLEWARE_CLASSES'] += ('mpowering.middleware.SearchFormMiddleware',)
    settings['TEMPLATE_CONTEXT_PROCESSORS'] += ('mpowering.context_processors.get_menu',)
    settings['CRISPY_TEMPLATE_PACK'] = 'bootstrap3'
    settings['SHOW_GRAVATARS'] = True
    settings['MPOWERING_GOOGLE_ANALYTICS_CODE'] = 'UA-58593028-1'
    
    settings['MPOWERING_ADMIN_EMAIL'] = 'alex@digital-campus.org'
    
    settings['TASK_UPLOAD_FILE_TYPES'] = ['pdf', 'vnd.oasis.opendocument.text','vnd.ms-excel','msword','application',]
    settings['TASK_UPLOAD_FILE_MAX_SIZE'] = "5242880"
    settings['DJANGO_WYSIWYG_FLAVOR'] = "tinymce_advanced"
    
    settings['HAYSTACK_CONNECTIONS'] = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        #'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        'URL': 'http://127.0.0.1:8983/solr/mpowering',
    }
    }                                  
    settings['HAYSTACK_SIGNAL_PROCESSOR'] = 'haystack.signals.RealtimeSignalProcessor'
    


