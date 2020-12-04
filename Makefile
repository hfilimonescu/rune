SHELL := /bin/bash

help:
	@echo " clean               Remove unwanted files like .pyc's"
	@echo " git_oneline         Extract the git log to git.log"
	@echo " req_save            Save pip export to requirements.txt"


clean:
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;
	find . -name '__pycache__' -exec rmdir --ignore-fail-on-non-empty {} \;

git_oneline:
	git log --pretty=format:"-   %s" > git.log

req_save:
	pip list --format=freeze | tee requirements/all.txt

req_upgrade:
	pip list --outdated --format=freeze | tee requirements/before_upgrade.txt | egrep -v '^(\-e|#)' | cut -d = -f 1  | xargs -n1 pip install -U
