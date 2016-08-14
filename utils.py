import math
from db import database_session


def custom_round(n, ndigits):
    part = n * 10 ** ndigits
    delta = part - int(part)
    # always round "away from 0"
    if delta >= 0.5 or -0.5 < delta <= 0:
        part = math.ceil(part)
    else:
        part = math.floor(part)
    return part / (10 ** ndigits)

def has_forecast_changed(model, results):
    with database_session() as session:
        most_recent = session.query(model)\
            .order_by(model.date_added.desc()).first()

        if most_recent:
            return most_recent.has_forecast_changed(results)

        return True