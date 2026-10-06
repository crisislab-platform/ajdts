# -*- coding: utf-8 -*-
"""Issues hosted directly by CRISiSLab.

To publish the next issue: drop its PDFs into new-issue/<dir>/, add an entry to
ISSUES (newest first) and re-run build.py. The first entry becomes the
"Current Issue"; any others are listed on the Previous Issues page above the
archived Massey volumes.
"""

# Stamped into the footer of every page. Bump it when you publish a change;
# leaving it to the build clock would make the output non-reproducible and the
# CI freshness check would fail the day after any commit.
UPDATED = "6 October, 2026"

ISSUES = [
    {
        "dir": "29-1",
        "volume": 29,
        "number": 1,
        "label": "Volume 29, Number 1",
        "year": "2026",
        "published": "March 2026",
        "subtitle": "",
        "full_pdf": "AJDTS_29_1_full.pdf",
        "contents_pdf": None,   # no separate contents PDF supplied
        "sections": [
            {
                "heading": "Research Papers",
                "papers": [
                    {
                        "pdf": "AJDTS_29_1_Woods.pdf",
                        "title": "Factors distinguishing treatment-seeking individuals and individuals who "
                                 "self-identified as coping well following the Canterbury Earthquake Sequence",
                        "authors": "Cate F. Woods, Virginia V. W. McIntosh, Christopher M. Frampton, "
                                   "Frances A. Carter, Janet D. Carter, Helen C. Colhoun, Jennifer Jordan, "
                                   "Rebekah A. Smith &amp; Caroline Bell",
                        "keywords": "Posttraumatic stress disorder, post-trauma outcomes, disaster, earthquake",
                        "page": 3,
                        "abstract":
                            "Following potentially traumatic events, most individuals do not develop mental "
                            "health issues and some even experience high levels of psychological functioning. "
                            "Others, however, develop mental health conditions such as posttraumatic stress "
                            "disorder (PTSD), depression, or anxiety disorders, and require specialist mental "
                            "health treatment. Few studies have directly compared individuals at these opposite "
                            "ends of the trauma response spectrum following the same event. The current study "
                            "identified factors distinguishing individuals seeking treatment for severe "
                            "earthquake-related distress (n = 184) and those who did not develop "
                            "earthquake-related distress and self-identified as coping well (n = 101) following "
                            "the 2010/11 Canterbury earthquake sequence. Participants completed measures of "
                            "sociodemographic factors, mental health history, earthquake exposure, life events, "
                            "and current psychological functioning. In univariate analyses, the groups reported "
                            "comparable levels of objective earthquake exposure, but treatment-seeking "
                            "participants reported significantly more pre-earthquake mental disorders, "
                            "peritraumatic distress (i.e., emotional and physiological distress experienced "
                            "during the earthquake), exposure-related distress (i.e., distress associated with "
                            "earthquake-related traumatic events), higher number of life events (e.g., marriage, "
                            "death of a family member) experienced in the past 5 years, and greater perceived "
                            "difficulty associated with life events. Treatment-seeking participants were also "
                            "significantly younger, more likely to be female, less likely to have a tertiary "
                            "educational qualification, and less likely to be in a relationship. In multivariate "
                            "analyses, peritraumatic distress and education level were the only factors that "
                            "uniquely distinguished the groups. Findings emphasise the importance of "
                            "peritraumatic experiences and education level in the development of distinct "
                            "post-trauma outcomes among individuals exposed to similar degrees of disaster "
                            "exposure. Subjective peritraumatic responses are likely to be useful to consider "
                            "in screening efforts following disasters.",
                    },
                    {
                        "pdf": "AJDTS_29_1_Pierce.pdf",
                        "title": "An educational activity on climate change for secondary students in Vanuatu: "
                                 "Does gender influence performance?",
                        "authors": "Charles Pierce",
                        "keywords": "Vanuatu, climate change, gender, discovery learning, secondary education, "
                                    "junior secondary level, climate resilience, climate change adaptation, "
                                    "mixed methods",
                        "page": 19,
                        "abstract":
                            "As part of wider research into the effectiveness of formal and traditional learning "
                            "about climate and disaster resilience in the Pacific Island nation of Vanuatu, a "
                            "mixed-method investigation was conducted during 2020 into the effectiveness of a "
                            "pictorial resource depicting key elements of climate change education used in a "
                            "discovery learning activity at junior secondary school level. Students completed a "
                            "questionnaire before and after the intervention so that changes in their knowledge, "
                            "attitudes, and behaviour could be measured. The quantitative data obtained was "
                            "supplemented by qualitative information from teachers on the reasons for patterns "
                            "observed. Results were compared across schools, age level, language of instruction, "
                            "gender, and urban/rural location; this paper focuses on comparisons by gender "
                            "obtained from a sample of 209 students, most of whom were in Years 9-10. While "
                            "average overall scores for boys and girls, both before and after the intervention, "
                            "were almost identical, girls performed better when their teacher was female and "
                            "boys when their teacher was male. Also, girls had significantly higher scores than "
                            "boys when the activity was conducted in urban schools, but not in rural schools. "
                            "Reasons for this difference include a tendency for boys to be more easily "
                            "distracted from their studies than girls in an urban environment.",
                    },
                    {
                        "pdf": "AJDTS_29_1_Lycos.pdf",
                        "title": "Experiences of children impacted by the 2019/2020 bushfires in South Australia: "
                                 "A qualitative study",
                        "authors": "Stella Lycos, Rachel M. Roberts, Anne Gannoni &amp; Susan Hamilton",
                        "keywords": "Disaster, children, bushfires, wildfires",
                        "page": 41,
                        "abstract":
                            "Little is known about children&rsquo;s subjective experiences of bushfires. This "
                            "study explores child experiences of South Australian bushfires that occurred during "
                            "2019/2020. Semi-structured interviews explored the experiences of children who "
                            "lived through the fires in the Adelaide Hills (n = 7) and Kangaroo Island (n = 2) "
                            "and were subsequently referred to a tertiary mental health service. Responses were "
                            "thematically analysed from a psychological perspective. Five themes were generated: "
                            "(1) planning, (2) separation, (3) fear of fire&rsquo;s destruction, (4) sense of a "
                            "close call, and (5) the fire left its mark. Children reported similar bushfire "
                            "experiences, and recalled the event as chaotic and frightening. Many experienced "
                            "brief separations from caregivers without means to communicate and conveyed a deep "
                            "concern for others&rsquo; safety including family and pets. Clinical care "
                            "practitioners should be aware of the specific fears and worries children experience "
                            "during disasters, and particularly, whether children experienced separation from a "
                            "caregiver. Furthermore, the presence and effect of pre-existing, co-occurring "
                            "negative life events and secondary stresses ought to be considered.",
                    },
                ],
            },
        ],
    },
]
