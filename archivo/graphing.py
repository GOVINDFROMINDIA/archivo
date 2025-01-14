from plotly.utils import PlotlyJSONEncoder
import plotly.graph_objects as go
from utils import stringTools
import datetime
import json
import os


def get_latest_stars_before_deadline(ont, deadline):
    sorted_versions = sorted(
        [v for v in ont.versions], key=lambda v: v.version, reverse=True
    )
    for version in sorted_versions:
        if version.version < deadline:
            return version.stars

    return None


def group_by_stars(ontologies, timespan=6, interval=2):
    dates = generate_dates(timespan=timespan, interval=interval)
    results = {}

    for deadline in dates:
        y_vals = {}
        # start with 0 stars each
        for i in range(5):
            y_vals[i] = 0
        for ont in ontologies:
            stars = get_latest_stars_before_deadline(ont, deadline)
            if stars != None:
                y_vals[stars] = y_vals.get(stars, 0) + 1
        results[deadline] = y_vals
    return dates, results


def generate_dates(timespan, interval):
    day = datetime.datetime.now()
    timedelta = datetime.timedelta(weeks=interval)
    dates = []
    needed_dates = int((timespan * 4) / interval) + 1
    # with timedelta 4 weeks -> 6 months in the past
    for i in range(needed_dates):
        dates.append(day)
        day = day - timedelta

    dates.reverse()
    return dates


def get_average_stars_from_dict(x_vals, results):
    average_star_values = []
    for day in x_vals:
        all_ont_count = sum([star_count for star_count in results[day].values()])
        denom = 0
        for stars, count in results[day].items():
            denom = denom + (stars * count)
        if all_ont_count > 0:
            average_star_values.append(denom / all_ont_count)
        else:
            average_star_values.append(0)
    return average_star_values


def generate_star_graph(ontologies, stats_path, timespan=6, interval=2):
    x_vals, results = group_by_stars(ontologies, timespan=timespan, interval=interval)
    figure = go.Figure()

    # four stars:
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=[results[d][4] for d in x_vals],
            name=stringTools.generateStarString(4),
            stackgroup="one",
            line=dict(width=0.5, color="rgb(34, 139, 34)"),
        )
    )
    # three stars:
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=[results[d][3] for d in x_vals],
            name=stringTools.generateStarString(3),
            stackgroup="one",
            line=dict(width=0.5, color="rgb(124, 252, 0)"),
        )
    )
    # two stars:
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=[results[d][2] for d in x_vals],
            name=stringTools.generateStarString(2),
            stackgroup="one",
            line=dict(width=0.5, color="rgb(255, 215, 0)"),
        )
    )
    # one star:
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=[results[d][1] for d in x_vals],
            name=stringTools.generateStarString(1),
            stackgroup="one",
            line=dict(width=0.5, color="rgb(255, 165, 0)"),
        )
    )
    # zero stars:
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=[results[d][0] for d in x_vals],
            name=stringTools.generateStarString(0),
            stackgroup="one",
            line=dict(width=0.5, color="rgb(255, 0, 0)"),
        )
    )
    # All onts
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=[sum([star_count for star_count in results[d].values()]) for d in x_vals],
            name="Total discovered ontologies",
            line=dict(width=1.0, color="rgb(0, 0, 0)"),
        )
    )
    # avergage stars
    figure.add_trace(
        go.Scatter(
            x=x_vals,
            y=get_average_stars_from_dict(x_vals, results),
            name="Average Stars",
            yaxis="y2",
            line=dict(width=1.0, color="rgb(0, 64, 255)", dash="dash"),
        )
    )
    figure.update_layout(
        yaxis=dict(
            title="Number of ontologies",
            # set range 50 more than latest number of ontologies (assumed that ontologies on archivo never decrease)
            range=[
                0,
                sum([star_count for star_count in results[x_vals[-1]].values()]) + 50,
            ],
        ),
        yaxis2=dict(
            title="Avgerage Stars",
            anchor="x",
            overlaying="y",
            side="right",
        ),
    )
    figure.update_layout(
        title_text="Archivo Stars Distribution",
        legend=dict(
            yanchor="top",
            x=1.35,
            xanchor="right",
            y=0.99,
        ),
    )
    with open(os.path.join(stats_path, "stars_over_time.json"), "w+") as json_file:
        json.dump(figure, json_file, cls=PlotlyJSONEncoder, indent=4)
