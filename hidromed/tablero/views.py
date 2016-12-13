# -*- coding: utf-8 -*-
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

#Vista de tablero rapido
@login_required
def TablerRapido(request):
	return render(request, 'pages/tablero.html')