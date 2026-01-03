import setuptools

setuptools.setup(
        name="qwer_replaypulse",
        version="2.0.0",
        description="RBLN-replayPulse",
        author="JunHui Ahn",
        author_email="june3780@rebellions.ai",
        packages=['qwer_replayPulse'],
        python_requires='>=3',
        install_requires=[
            'pandas',
            'matplotlib',
            'pytz'
        ],
        entry_points={
            'console_scripts':[
                'rbln-replayPulse = rbln_replayPulse.main:main'
            ]
        }
)
