from datetime import datetime
from typing import List

STAT_OUTPUT = '{source} analysis results:\n' \
               'Average release time: {average}\n' \
               'Median release time: {median}\n' \
               'Number of releases: {releases_number}\n' \
               'First release date: {fst_release_date}\n' \
               'Last release date: {lst_release_date}.'


def calc_stat(v_timestamps: List[datetime], source: str):
    releases_number = len(v_timestamps)
    if releases_number == 0:
        return f'{source} has no release history'
    if releases_number == 1:
        return STAT_OUTPUT.format(
            source=source,
            releases_number=releases_number,
            average=None, median=None,
            fst_release_date=v_timestamps[0],
            lst_release_date=v_timestamps[0])

    last_release_time = v_timestamps[0]
    first_release_time = v_timestamps[-1]

    release_intervals = []
    previous_release_date = last_release_time
    for i in range(1, releases_number):
        current_release_date = v_timestamps[i]
        release_intervals.append((previous_release_date - current_release_date).days)
        previous_release_date = current_release_date

    release_intervals = list((filter(lambda time: time != 0, release_intervals)))

    average_release_time = int(sum(release_intervals) / len(release_intervals))

    release_intervals.sort()
    median_release_time = release_intervals[int(len(release_intervals) / 2)]

    return STAT_OUTPUT.format(
        source=source,
        releases_number=releases_number,
        average=average_release_time,
        median=median_release_time,
        fst_release_date=last_release_time.date(),
        lst_release_date=first_release_time.date())

