from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3qz424r6^spn(i%eg1w38l(-z#2fzgf6e70es@y#+tvl5e93gg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*","127.0.0.1","localhost","kijeka.com"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3001",
    "http://localhost:8080",
    "https://kijeka.com",
    "http://*:*",
    "https://*:*",
    "https://fluffy-rotary-phone-g9rw4jq57qgh9477-3000.app.github.dev",
    "https://fluffy-rotary-phone-g9rw4jq57qgh9477-8000.app.github.dev"
]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3001",
    "http://localhost:8080",
    "https://kijeka.com",
    "http://*:*",
    "https://*:*",
    "https://fluffy-rotary-phone-g9rw4jq57qgh9477-3000.app.github.dev",
    "https://fluffy-rotary-phone-g9rw4jq57qgh9477-8000.app.github.dev"
]

 # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
 # SECURE_SSL_REDIRECT = True
 # SESSION_COOKIE_SECURE = True
 # CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kijeka.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kijeka.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    
}

# 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'defaultdb',
    #     'USER': 'doadmin',
    #     'PASSWORD': 'AVNS_L0wb3hpB7P36Pihn35A',
    #     'HOST': 'db-postgresql-blr1-83025-do-user-13735066-0.b.db.ondigitalocean.com',
    #     'PORT': '25060',
    #     'OPTIONS': {
    #         'sslmode': 'require',
    #         'sslrootcert': 'ca-certificate.crt',
    #         },
    # }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

MEDIA_ROOT =  os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SECRET_KEY = '6LcP1-wkAAAAAPEyR0wxSXO6cLpmiF3jfqI-JcL-'
SITE_KEY = '6LcP1-wkAAAAAJ7rGFlQwmL4DvUvmfIj6FljoNrX'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jaivin@pruthatek.com'
EMAIL_HOST_PASSWORD = 'Jaivin@123'

#github repo  https://github.com/Anshmodi30/test001.git
