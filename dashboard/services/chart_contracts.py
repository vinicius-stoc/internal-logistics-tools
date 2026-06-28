def make_chart_contract(chart_id, title, chart_type, labels, datasets, options=None):
    return {
        "id": chart_id,
        "title": title,
        "type": chart_type,
        "data": {
            "labels": list(labels),
            "datasets": list(datasets),
        },
        "options": options or {},
    }


def make_single_dataset_chart(chart_id, title, chart_type, labels, label, data, options=None):
    return make_chart_contract(
        chart_id=chart_id,
        title=title,
        chart_type=chart_type,
        labels=labels,
        datasets=[
            {
                "label": label,
                "data": list(data),
            }
        ],
        options=options,
    )
