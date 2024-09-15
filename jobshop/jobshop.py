

###### Leitura de arquivo #####
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

df = pd.read_csv('jobs.csv')

df.set_index('Job', inplace=True)

jobs = df

print(">>> jobs")
print(jobs)

#####################

df = pd.read_csv('schedule.csv')
df.set_index('Job', inplace=True)
schedule_optimal = df.rename(columns={'Start': 'start', 'Finish': 'finish', 'Past': 'past'})

# Exibindo o resultado
print(">>> schedule optimal")
print(schedule_optimal)

#####################

def schedule_jobs(jobs, seq):
    """
    Schedule a sequence of jobs based on their release times, durations, and due times.

    Args:
        jobs (DataFrame): Job information with columns "release", "duration", and "due".
        seq (DataFrame): A list of job indices representing the sequence in which the jobs will be scheduled.

    Return:
        A DataFrame containing schedule information, including "start", "finish", and "past" due times.
    """
    schedule = pd.DataFrame(index=jobs.index)
    t = 0
    for job in seq:
        t = max(t, jobs.loc[job]["release"])
        schedule.loc[job, "start"] = t
        t += jobs.loc[job, "duration"]
        schedule.loc[job, "finish"] = t
        schedule.loc[job, "past"] = max(0, t - jobs.loc[job, "due"])

    return schedule

schedule = schedule_jobs(jobs, jobs.index)
schedule

def gantt(jobs, schedule, title="Job Schedule"):
    """
    Plot a Gantt chart for a given job schedule.

    Args:
        jobs (DataFrame): Contains job release times and due times.
        schedule (DataFrame): Contains  job start times, finish times, and past due times.
        title (str, optional): Title of the Gantt chart. Defaults to "Job Schedule".
    """
    w = 0.25  # bar width
    fig, ax = plt.subplots(1, 1, figsize=(10, 0.7 * len(jobs.index)))

    for k, job in enumerate(jobs.index):
        r = jobs.loc[job, "release"]
        d = jobs.loc[job, "due"]
        s = schedule.loc[job, "start"]
        f = schedule.loc[job, "finish"]

        # Show job release-due window
        ax.fill_between(
            [r, d], [-k - w, -k - w], [-k + w, -k + w], lw=1, color="k", alpha=0.2
        )
        ax.plot(
            [r, r, d, d, r], [-k - w, -k + w, -k + w, -k - w, -k - w], lw=0.5, color="k"
        )

        # Show job start-finish window
        color = "g" if f <= d else "r"
        ax.fill_between(
            [s, f], [-k - w, -k - w], [-k + w, -k + w], color=color, alpha=0.6
        )
        ax.text(
            (s + f) / 2.0,
            -k,
            "Job " + job,
            color="white",
            weight="bold",
            ha="center",
            va="center",
        )

        # If past due
        if f > d:
            ax.plot([d] * 2, [-k + w, -k + 2 * w], lw=0.5, color="k")
            ax.plot([f] * 2, [-k + w, -k + 2 * w], lw=0.5, color="k")
            ax.plot([d, f], [-k + 1.5 * w] * 2, solid_capstyle="butt", lw=1, color="k")
            ax.text(
                f + 0.5,
                -k + 1.5 * w,
                f"{schedule.loc[job, 'past']} past due",
                va="center",
            )

    total_past_due = schedule["past"].sum()
    ax.set_ylim(-len(jobs.index), 1)
    ax.set_title(f"{title}: Total past due = {total_past_due}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Jobs")
    ax.set_yticks([])  # range(len(jobs.index)), jobs.index)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["top"].set_visible(False)

    custom_lines = [
        Line2D([0], [0], c="k", lw=10, alpha=0.2),
        Line2D([0], [0], c="g", lw=10, alpha=0.6),
        Line2D([0], [0], c="r", lw=10, alpha=0.6),
    ]
    ax.legend(
        custom_lines,
        ["Job release/due window", "Completed on time", "Completed past due"],
    )


gantt(jobs, schedule, "Execute Jobs in Order")
plt.show()

fifo = schedule_jobs(jobs, jobs.sort_values(by="release").index)
gantt(jobs, fifo, "First in, First out")
plt.show()

edd = schedule_jobs(jobs, jobs.sort_values(by="due").index)
gantt(jobs, edd, "First in, First out")
plt.show()

gantt(jobs, schedule_optimal, "Optimized Jobs Order")
plt.show()