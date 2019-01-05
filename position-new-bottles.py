#!/usr/bin/env python3

# This script loads the cellar and positions all bottles with empty
# coordinates. This differs from defragmentation in that it will not move any
# bottle that currently has a position

# --------------------------------------------------------------------------------

from backend.raw import db
from backend.cellar import Cellar
from scripts.confirm import confirmAndCommit

cellar = Cellar()
layout = cellar.computeLayout()
layout.positionBottles(cellar.logger)

confirmAndCommit(db, cellar.logger)
