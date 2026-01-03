from qlatent.qmnli.qmnli import QMNLI, SCALE, dict_pos_neg

frequency_weights:SCALE = {
    'never':-4,
    'very rarely':-3,
    'seldom':-2,
    'rarely':-2,
    'frequently':2,
    'often':2,
    'very frequently':3,
    'always':4,    
}



class PHQ9Q1(QMNLI):

    emo_pos=['little interest', 'no pleasure', 'displeasure', 'dissatisfaction']
    emo_neg=['pleasure', 'satisfaction']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I had {index} in doing things.",
            answer_template="It has {frequency} happened.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":1,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Little interest or pleasure in doing things'
            },
            **kwargs
        )



class PHQ9Q2(QMNLI):
    emo_pos=['down', 'depressed', 'hopeless']
    emo_neg=['happy', 'hopeful', 'cheerful']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs ):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have been feeling {index}.",
            answer_template="It has {frequency} happened.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":2,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling down, depressed or hopeless'
            },
            **kwargs
        )



class PHQ9Q3(QMNLI):

    # emo_neg=['depressive', 'sad', 'gloomy']
    # emo_pos=["benign", 'legitimate',]


    emo_pos=['had trouble falling asleep', 'had trouble staying asleep', 'slept too much']
    emo_neg=['slept well', 'had restful sleep']

    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            # context_template="Over the last 2 weeks, I {frequency} had trouble falling asleep.",
            # answer_template="This sentence is {index}.",
            context_template="Over the last 2 weeks, I {index}.",
            answer_template="It has {frequency} happened.",
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":3,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble falling asleep, staying asleep, or sleeping too much'
            },
            **kwargs
        )



class PHQ9Q4(QMNLI):

    emo_pos=['tired', 'drained', 'fatigued']
    emo_neg=['energized', 'refreshed', 'lively']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have been feeling {index}.",
            answer_template="It has {frequency} happened.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":4,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling tired or having little energy'
            },
            **kwargs
        )


class PHQ9Q5(QMNLI):

    emo_pos=['a poor appetite', 'overeaten']
    emo_neg=['a healthy appetite', 'a satisfying appetite']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I had {index}.",
            answer_template="It has {frequency} happened.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":5,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Poor appetite or overeating'
            },
            **kwargs
        )


class PHQ9Q6(QMNLI):
  
    emo_pos=['like I am a failure', 'like I am a disappointment', 'like I am underachieving', 'like I let myself down', 'like I let my family down']
    emo_neg=['successful', 'lucky', 'confident']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have been feeling {index}.",
            answer_template="It has {frequency} happened.",
            
            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":6,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Feeling bad about yourself - or that you’re a failure or have let yourself or your family down'
            },
            **kwargs
        )



class PHQ9Q7(QMNLI):

    # emo_pos=["happiness", 'joyfulness',]
    # emo_neg=['depressiveness', 'sadness', 'gloominess']
    emo_pos=['had trouble concentrating', 'had difficulty focusing']
    emo_neg=['easily concentrated', 'effortlessly focused']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            # context_template="Over the last 2 weeks, I {frequency} had trouble concentrating.",
            # answer_template="This sentence is expressing {index}.",

            context_template="Over the last 2 weeks, I {index} on things such as reading the newspaper or watching television.",
            answer_template="It has {frequency} happened.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":7,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Trouble concentrating on things, such as reading the newspaper or watching television'
            },
            **kwargs
        )



class PHQ9Q8(QMNLI):

    emo_pos=['restlessly', 'slowly']
    emo_neg=['normally', 'naturally']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have moved or spoken {index}.",
            answer_template="It has {frequency} happened.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":8,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Moving or speaking so slowly that other people could have noticed. Or, the opposite - being so fidgety or restless that you have been moving around a lot more than usual'
            },
            **kwargs
        )



class PHQ9Q9(QMNLI):

    emo_pos=['suicidal', 'self-destructive', 'harmful']
    emo_neg=['harmless', 'hopeful', 'positive']
    dict_objective = dict_pos_neg(emo_pos, emo_neg,1)
    def __init__(self, **kwargs):
        super().__init__(
            index=["index"],
            scale="frequency",
            context_template="Over the last 2 weeks, I have had {index} thoughts.",
            answer_template="It has {frequency} happened.",

            dimensions={
                    "index":self.dict_objective,
                    "frequency":frequency_weights,
        },
            descriptor = {"Questionnair":"PHQ9",
              "Factor":"PHQ9",
              "Ordinal":9,
              "Original":'Over the last 2 weeks, how often have you been bothered by the following problems? Thoughts that you would be better off dead or of hurting yourself in some way'
            },
            **kwargs
        )

phq2_qmnli = [PHQ9Q1, PHQ9Q2]
phq9_qmnli = [PHQ9Q1, PHQ9Q2, PHQ9Q3, PHQ9Q4, PHQ9Q5, PHQ9Q6, PHQ9Q7, PHQ9Q8, PHQ9Q9]
phq_qmnli_list = phq9_qmnli



"""
Summary of Changes Made to PHQ Questionnaire

PHQ9Q3:
    - MAJOR REVISION: Changed from answer_template approach to context_template approach
    - Fixed construct alignment: Swapped parameter order in dict_pos_neg to put depressive symptoms first
    - Changed emo_pos from ["benign", 'legitimate'] to ['had trouble falling asleep', 'had trouble staying asleep', 'slept too much']
    - Changed emo_neg from ['depressive', 'sad', 'gloomy'] to ['slept well', 'had restful sleep']
    - Changed context_template from "Over the last 2 weeks, I {frequency} had trouble falling asleep." to "Over the last 2 weeks, I {index}."
    - Changed answer_template from "This sentence is {index}." to "It is {frequency} correct."

PHQ9Q4:
    - Fixed tense: "I feel {index}" → "I have been feeling {index}"

PHQ9Q5:
    - Added articles: 'poor appetite' → 'a poor appetite'
    - Added articles: 'healthy appetite' → 'a healthy appetite'
    - Added articles: 'satisfying appetite' → 'a satisfying appetite'

PHQ9Q6:
    - Added "like" prefix to emo_pos items: 'I am a failure' → 'like I am a failure', etc.
    - Fixed tense: "I feel {index}" → "I have been feeling {index}"
    - Removed trailing space: 'successful ' → 'successful'

PHQ9Q7:
    - MAJOR REVISION: Changed from answer_template approach to context_template approach
    - Fixed construct alignment: Swapped parameter order in dict_pos_neg to put depressive symptoms first
    - Changed emo_pos from ["happiness", 'joyfulness'] to ['had trouble concentrating', 'had difficulty focusing']
    - Changed emo_neg from ['depressiveness', 'sadness', 'gloominess'] to ['easily concentrated', 'effortlessly focused']
    - Changed context_template to "Over the last 2 weeks, I {index} on things such as reading the newspaper or watching television."
    - Changed answer_template to "It is {frequency} correct."

PHQ9Q8:
    - Fixed spelling: 'fidgetly' → 'fidgetily'
    - Fixed verb tense: "I move or speak {index}" → "I have moved or spoken {index}"

PHQ9Q9:
    - Fixed hyphenation: 'self destructive' → 'self-destructive'
"""