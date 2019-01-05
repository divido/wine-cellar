#!/usr/bin/env python3

# This script clears all bottle positions, then repositions them within the
# cellar. It will rebalance the cellar if bottles have gotten clustered, and
# will importantly move bottles forward as they become ready to drink.

# --------------------------------------------------------------------------------

from backend.raw import db
from backend.cellar import Cellar
from scripts.confirm import confirmAndCommit

cellar = Cellar()
cellar.clearBottlePositions()

layout = cellar.computeLayout()
layout.positionBottles(cellar.logger)

confirmAndCommit(db, cellar.logger)
