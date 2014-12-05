from bokeh.plotting import output_file, show, scatter
from bokeh.models import ColumnDataSource, DataRange1d, Plot, LinearAxis, Grid, GlyphRenderer, Circle, HoverTool, BoxSelectTool
from bokeh.models.widgets import VBox, DataTable, TableColumn, StringFormatter, NumberFormatter, StringEditor, IntEditor, NumberEditor, SelectEditor
from os.path import dirname, join
from bokeh.models.widgets.tables import StringEditor
import pandas.io.date_converters as conv
from time import strftime
import pandas as pd
from bokeh.models.plots import Plot
from bokeh.charts.scatter import Scatter
from numpy import linspace, long
from datetime import datetime, timedelta
import numpy as np


def parse_dates(x):
    return [datetime.strptime(z, '%m-%d-%Y %H:%M:%S') for z in x]


def color_code(x):
    r = []
    for z in x:
        c = "000000"
        if z:
            try:
                if z > 0.0:
                    c = "11111"
            except:
                pass
        r.append(c)
    return r

output_file('data_tables.html', title='Data Tables')

data = pd.read_csv(
    'c:\\temp\\loans\\browseNotes_1-RETAIL.csv', parse_dates=True, index_col=False)
data['funded_perc'] = 100.0 * data['funded_amnt'] / data['loan_amnt']
data['a'] = parse_dates(data['exp_d'])
now = datetime.now()
data['b'] = [
    -(now - d).days - (d - now).seconds / 60 / 60 / 24 for d in data['a']]
data['RiskInt'] = 100 * ((data['effective_int_rate'] / 100 + 1)
                         * (1 - data['exp_default_rate'] / 100) - 1)
data['pct_tl_nvr_dlq'] = (.01 * data['pct_tl_nvr_dlq']) ** 4
# data['bc_util'] = data.bc_util.map(float)

'''
dqy += "WHERE (bc_util*1 < 85) "
dqy += "AND (revol_util*1 < 85) "
dqy += "AND (num_accts_ever_120_pd='0') "
dqy += "AND (annual_inc -40000 >0) "
dqy += "AND (grade>'C') "
dqy += "AND (purpose<>'Business' And purpose<>'Medical expenses') "
dqy += "AND (delinq_2yrs='0') "
dqy += "AND (acc_open_past_24mths*1 < 6) "
dqy += "AND (inq_last_6mths<'2') "
dqy += "AND (tot_coll_amt='0') "
dqy += "AND (num_tl_120dpd_2m='0') "
dqy += "AND (tax_liens='0') "
dqy += "AND (pub_rec='0') "
dqy += "AND (collections_12_mths_ex_med='0') "
dqy += "AND (chargeoff_within_12_mths='0') "
dqy += "AND (pub_rec_bankruptcies='0') "
'''
# print(data['filter'])
source = ColumnDataSource(data)
columns = [
    TableColumn(field="list_d", title="list_d"),
    TableColumn(field="loan_amnt", title="loan_amnt",
                formatter=NumberFormatter(format="0.0")),
    TableColumn(field="funded_amnt", title="funded_amnt",
                formatter=NumberFormatter(format="0.0")),
    TableColumn(field="int_rate", title="int_rate",
                formatter=NumberFormatter(format="0.00")),
    TableColumn(field="sub_grade", title="sub_grade"),
    TableColumn(field="emp_title", title="emp_title"),
    TableColumn(field="annual_inc", title="annual_inc",
                formatter=NumberFormatter(format="0")),
    TableColumn(field="addr_state", title="addr_state"),
    TableColumn(field="title", title="title"),
    TableColumn(
        field="mths_since_last_delinq", title="mths_since_last_delinq"),
    TableColumn(field="mo_sin_rcnt_tl", title="mo_sin_rcnt_tl"),
    TableColumn(field="bc_util", title="bc_util"),
    TableColumn(field="dti", title="dti"),
]
data_table = DataTable(source=source, columns=columns)
xdr = DataRange1d(sources=[source.columns("b")])
ydr = DataRange1d(sources=[source.columns("funded_perc")])
plot = Plot(title=None, x_range=xdr, y_range=ydr,
            plot_width=1000, plot_height=600)
xaxis = LinearAxis(plot=plot)
plot.below.append(xaxis)
yaxis = LinearAxis(plot=plot)
ygrid = Grid(plot=plot, dimension=1, ticker=yaxis.ticker)
plot.left.append(yaxis)
# dat_glyph = Circle(x="b", y="funded_perc",
# fill_color="#396285", size=8, fill_alpha=1, line_alpha=0.0)
dat_glyph = Circle(x="b", y="funded_perc",
                   fill_color="#396285", size='RiskInt', fill_alpha='pct_tl_nvr_dlq', line_alpha='dti')
dat = GlyphRenderer(data_source=source, glyph=dat_glyph)

tooltips = [
    ("Listed", "@list_d"),
    ("Funded", "$" + "@funded_amnt" + " of $" +
     "@loan_amnt" + " [" + "@funded_perc" + "%]"),
    ("Purpose", "@title"),
    ("Income", "$" + "@annual_inc" + ", " +
     "@emp_title" + ", " + "@emp_length" + " [" + "@addr_state" + "]"),
    ("acc_open_past_24mths", "@acc_open_past_24mths"),
    ("percent_bc_gt_75", "@percent_bc_gt_75"),
    ("earliest_cr_line", "@earliest_cr_line"),
    ("Recent Inquiries", "@inq_last_6mths" +
     " (last one: " + "@mths_since_recent_inq" + " months ago)"),
    ("earliest_cr_line", "@earliest_cr_line"),
    ("bc_util", "@bc_util"),
    ("dti", "@dti"),
]
'''
num_sats    open_acc
num_tl_90g_dpd_24m
num_tl_30dpd
total_bc_limit    bc_open_to_buy    total_rev_hi_lim    revol_bal    total_il_high_credit_limit    tot_hi_cred_lim    total_bal_ex_mort    tot_cur_bal    avg_cur_bal
mths_since_recent_revol_delinq
mths_since_recent_bc_dlq
+ mo_sin_rcnt_tl
+ mths_since_last_delinq
++ pct_tl_nvr_dlq
++ CcUtil    RevolUtil    DtiPrc

dat_hover_tool = HoverTool(plot=plot, renderers=[dat], tooltips=tooltips + [("UsageCpuGHz", "@UsageCpuGHz")])
mem_hover_tool = HoverTool(plot=plot, renderers=[mem], tooltips=tooltips + [("UsageMemoryGB", "@UsageMemoryGB")])
select_tool = BoxSelectTool(plot=plot, renderers=[dat, mem], dimensions=['width'])
plot.tools.extend([dat_hover_tool, mem_hover_tool, select_tool])
plot.renderers.extend([dat, mem, ygrid])
'''
dat_hover_tool = HoverTool(
    plot=plot, renderers=[dat], tooltips=tooltips + [("sub_grade", "@sub_grade")])
select_tool = BoxSelectTool(plot=plot, renderers=[dat], dimensions=['width'])
plot.tools.extend([dat_hover_tool, select_tool])
plot.renderers.extend([dat, ygrid])

layout = VBox(plot, data_table)
show(layout)
