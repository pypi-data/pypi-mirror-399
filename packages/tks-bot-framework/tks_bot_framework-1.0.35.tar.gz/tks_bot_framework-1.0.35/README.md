# tks-bot-framework
This framework is the basis of every bot. Be it trend-following, ARIMA or AI/ML.

## TODO 
- [ ] Add a push query to listen to updates from Freya Alpha (i.e. the fa-signal-service) and to process them.
- [ ] Add a function that evokes an alert if a sent signal is not confirmed by Freya Alpha within a time threshold.
- [ ] Adapt push_query function to include a WHERE statement:
    push_query = f"""
    SELECT {select_columns} FROM {stream_name}
    WHERE provider_id = '{provider_id_filter}'
    EMIT CHANGES;
    """
    This push_query will be used in a logic that keeps track of the flow of the messages.
- [ ] Parametrize URLs.
- [ ] Reinstall tks-essentials (kafka cluster reduced to single broker for development).
- [ ] Decide on partitions (kafka/sqldb).
- [ ] Decide on keys (kafka/sqldb).
- [ ] Parametrize for exchanges.
- [ ] Grooming of imports, versioning.
- [ ] Adapt commented out tests in test_market_mgr.py (adapt to removed imports)

## General
Run and compiled for Python 3.9.13.

## Development

### Installation as Consuming Developer

Simply run: `pip install tks-bot-framework`

All the required libraries must be listed in requirements.txt and installed by  `py -m pip install -r .\requirements.txt`

Import in modules without the dash (e.g.): `from botframework.portfolio_mgr import PortfolioMgr`

### Setup as Contributor
Create the virtul environment: `py -m venv .venv`
Start the Environment: `./.venv/Scripts/activate`. Use `deactivate`to stop it.
Update the PIP: `py -m pip install --upgrade pip`

All the required libraries must be listed in requirements.txt and installed by  `py -m pip install -r .\requirements.txt`

To cleanup the environment run:
`pip3 freeze > to-uninstall.txt` and then
`pip3 uninstall -y -r to-uninstall.txt`

or `pip3 install pip-autoremove`

### Debug
Simply run the app in debug mode using the existing launch.json (Ctrl+Shift+D) and then run the app with F5.

### Build Library
Prerequisite: make sure that you give your Operating System user the right to modify files in the python directory. The directory where pyhton is installed.
Use `python setup.py bdist_wheel` to create the dist, build and .eggs folder.

## Reference from a different project
In order to use your own version of the project - to maybe contribute to the framework - simply clone the code from github into new directory. Then add the path of that new directory to the requirements.txt file of your project. Then change in botframework whatever you recommend to improve. Don't forget the Open-Closed Principle: extend only (unless it requires a breaking change)

### Releasing a new version

Update the version in the pyproject.toml.

Delete any old files in the /dist folder.
Update your pip: `python -m pip install --upgrade pip`

Install the tools build, twine and bumpver: `python -m pip install build twine bumpver`
Upgrade the setuptools: `pip install --upgrade setuptools`

Bump the version in pyproject.toml: `bumpver update --patch`

Build the project: `python -m build`

Check the distribution: `twine check dist/*`

Upload to test-pypi to validate: `twine upload -r testpypi dist/*`

Login with username: svabra (password should be known)

If the test-upload was successful, finally, upload to pypi production: `twine upload dist/*`

Done.

(P.S. Do not forget to update the framework in your projects: `pip install --upgrade tks-bot-framework`)