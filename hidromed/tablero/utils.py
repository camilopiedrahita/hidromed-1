# -*- coding: utf-8 -*-
import datetime
import numpy as np
import pandas as pd

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import AreaChart, ColumnChart
from dateutil.relativedelta import relativedelta

from hidromed.izarnet.models import Izarnet
from hidromed.medidores.models import Medidor
from hidromed.users.models import Poliza_Medidor_User

