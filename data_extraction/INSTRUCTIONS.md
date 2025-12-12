# Instructions for /bflow page on frontend

- Data will be taken for this page from server from /data_hu_dashboard, /data_lines_dashboard, /data_hu_pgi_dashboard, /data_lines_pgi_dashboard
- On the middle of the card we will use data from /data_hu_dashboard and /data_hu_pgi_dashboard
- Data looks like this:
```
"12.12.2025": {
        "ground_floor": {
            "picked": {
                "amount_of_hu": 253
            },
            "not_picked": {
                "amount_of_hu": 189
            }
        },
        "first_floor": {
            "picked": {
                "amount_of_hu": 245
            },
            "not_picked": {
                "amount_of_hu": 375
            }
        },
        "second_floor": {
            "picked": {
                "amount_of_hu": 379
            },
            "not_picked": {
                "amount_of_hu": 642
            }
        },
        "picked": {
            "amount_of_hu": 876
        },
        "not_picked": {
            "amount_of_hu": 1206
        }
    }
```
- In the middle make a number that will represent how many handling units are open, that means the sum of amount_of_hu under the 'picked' and 'not_picked'
- Under it, like a subtext, a text and a number saying 'Of which {number_1} not fully picked and {number_2} fully picked' where number_1 will be amount_of_hu under 'not_picked' in a red color and number_2 will be amount_of_hu under 'picked' in a orange color
- Under this another text saying '{number_3} handling units PGI' where number_3 will be from amount_of_hu_pgi from data_hu_pgi_dashboard which looks like this:
```
"12.12.2025": {
        "ground_floor": {
            "amount_of_hu_pgi": 1188
        },
        "first_floor": {
            "amount_of_hu_pgi": 1712
        },
        "second_floor": {
            "amount_of_hu_pgi": 1328
        },
        "amount_of_hu_pgi": 4228
    }
```
- Small note, hu PGI is only available for today's date so when we move between Backlog or Future we will not show this part

- On the right side of the card we will use data from /data_lines_dashboard and /data_lines_pgi_dashboard
- Data looks like this:
```
"12.12.2025": {
        "ground_floor": {
            "picked": {
                "amount_of_lines": 531
            },
            "not_picked": {
                "amount_of_lines": 464
            }
        },
        "first_floor": {
            "picked": {
                "amount_of_lines": 567
            },
            "not_picked": {
                "amount_of_lines": 1194
            }
        },
        "second_floor": {
            "picked": {
                "amount_of_lines": 744
            },
            "not_picked": {
                "amount_of_lines": 1410
            }
        },
        "picked": {
            "amount_of_lines": 1842
        },
        "not_picked": {
            "amount_of_lines": 3068
        }
    },
```
- In the middle make a number that will represent how many lines are open, that means the sum of amount_of_lines under the 'picked' and 'not_picked'
- Under it, like a subtext, a text and a number saying 'Of which {number_1} not picked and {number_2} not PGI' where number_1 will be amount_of_lines under 'not_picked' in a red color and number_2 will be amount_of_lines under 'picked' in a orange color
- Under this another text saying '{number_3} lines PGI' where number_3 will be from amount_of_lines_pgi from data_lines_pgi_dashboard which looks like this:
```
"12.12.2025": {
        "ground_floor": {
            "amount_of_lines_pgi": 2338
        },
        "first_floor": {
            "amount_of_lines_pgi": 3448
        },
        "second_floor": {
            "amount_of_lines_pgi": 3193
        },
        "amount_of_lines_pgi": 8979
    }
```
- Small note, hu PGI is only available for today's date so when we move between Backlog or Future we will not show this part