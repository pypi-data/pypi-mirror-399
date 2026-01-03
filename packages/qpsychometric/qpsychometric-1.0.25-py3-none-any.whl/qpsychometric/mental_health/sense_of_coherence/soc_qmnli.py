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

class SOCQ4(QMNLI):
  


  kw_attitude_neg = ["meaningless", "dull", "aimless", 'boring']
  kw_attitude_pos = ["meaningful", "interesting", "fulfilling", 'fascinating']
  dict_attitude = dict_pos_neg(kw_attitude_pos,kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="What goes on around me is {index} to me.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":4,
                      "Original":"Do you have the feeling that you don't really care what goes on around you? "
        },
        **kwargs,
    )

class SOCQ5(QMNLI):
  


  kw_attitude_neg = ['surprised by','puzzled by']
  kw_attitude_pos = ['expecting','anticipating']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I am {frequency} {index} the behavior of people I thought I knew well.",
        answer_template="True.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":5,
                      "Original":"Has it happened in the past that you were surprised by the behavior of people whom you thought you knew well? "
        },
        **kwargs,
    )

class SOCQ6(QMNLI):
  


  kw_attitude_neg = ["disappointed", 'failed']
  kw_attitude_pos = ["supported", "helped"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="People whom I counted on {frequency} {index} me.",
        answer_template="True.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":6,
                      "Original":"Has it happened that people whom you counted on disappointed you? "
        },
        **kwargs,
    )

class SOCQ8(QMNLI):


  kw_attitude_neg = ["meaningless", "aimless", 'pointless']
  kw_attitude_pos = ["meaningful", "significant", 'purposeful']

  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="My life is {index}.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":8,
                      "Original":"Until now your life has had: "
        },
        **kwargs,
    )

class SOCQ9(QMNLI):


  kw_attitude_neg = ["unfairly", "unjustly", "with discrimination", "unequally"]
  kw_attitude_pos = ["fairly", "justly", "equally"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I feel that I am being treated {index}.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":9,
                      "Original":"Do you have the feeling that you're being treated unfairly? "
        },
        **kwargs,
    )

class SOCQ12(QMNLI):
  


  kw_attitude_neg = ["helpless", "hopeless", 'powerless']
  kw_attitude_pos = ["at ease", "comfortable", "relaxed"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="In unfamiliar situations I feel {index}.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":12,
                      "Original":"Do you have the feeling that you're in an unfamiliar situation and don't know what to do?"
        },
        **kwargs,
    )

class SOCQ16(QMNLI):


  kw_attitude_neg = ["meaningless", "aimless", 'boring']
  kw_attitude_pos = ["meaningful", "interesting", "fulfilling", 'fascinating']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="Doing the things I do every day is {index}.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":16,
                      "Original":"Doing the things you do every day is: "
        },
        **kwargs,
    )

class SOCQ19(QMNLI):
  


  kw_attitude_pos = ["clear", "coherent", "distinct"]
  kw_attitude_neg = ["mixed-up", "confused", "unclear"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="My feelings and ideas are very {index}.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":19,
                      "Original":"Do you have very mixed-up feelings and ideas? "
        },
        **kwargs,
    )

class SOCQ21(QMNLI):
  


#   kw_attitude_pos = ['face', 'confront', 'acknowledge', 'process', 'accept']
#   kw_attitude_neg = ['ignore', 'avoid', 'dismiss']
  kw_attitude_pos = ['face', 'feel', 'acknowledge']
  kw_attitude_neg = ['ignore', 'avoid', 'dismiss']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I would rather {index} the feelings inside of me.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":21,
                      "Original":"Does it happen that you have feelings inside you would rather not feel? "
        },
        **kwargs,
    )

class SOCQ25(QMNLI):
  


  kw_attitude_neg = ["failure", "loser", "sad sack", "worthless person"]
  kw_attitude_pos = ["winner", "successful person", "valuable person"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="Even though I have a strong character, in ceratin situations I feel like a {index}.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":25,
                      "Original":"Many people—even those with a strong character—sometimes feel like sad sacks (losers) in certain situations. How often have you felt this way in the past? "
        },
        **kwargs,
    )

class SOCQ26(QMNLI):
  

  kw_attitude_pos = ["accurately estimate", "correctly judge"]
  kw_attitude_neg = ["overestimate","misjudge",'underestimate']
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I {index} the importance of something that happened.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Comprehensibility",
                      "Ordinal":26,
                      "Original":"When something happened, you have generally found that: you overestimated or underestimated its importance, you saw things in the right proportion"
        },
        **kwargs,
    )

class SOCQ28(QMNLI):
  


  kw_attitude_neg = ["little", "minimal", "negligible"]
  kw_attitude_pos = ["great", "significant", "deep"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        context_template="I find {index} meaning in my daily life.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Meaningfulness",
                      "Ordinal":28,
                      "Original":"How often do you have the feeling that there's little meaning in the things you do in your daily life? "
        },
        **kwargs,
    )

class SOCQ29(QMNLI):


#   kw_attitude_neg = ["out of control", "uncontrollable", 'unmanageable']
#   kw_attitude_pos = ["under control", "stable", "regulated"]
#   kw_attitude_pos = ["positive", "sure", 'certain', 'confident']
#   kw_attitude_neg = ["doubtful", "uncertain", "unconvinced"]
  kw_attitude_pos = ["positive", "sure", 'certain', 'confident']
  kw_attitude_neg = ["doubtful", "uncertain", "unconvinced"]
  dict_attitude = dict_pos_neg(kw_attitude_pos, kw_attitude_neg, 1.0)

  def __init__(self, **kwargs):
    super().__init__(
        index=["index"],
        scale="frequency",
        # context_template="My feelings are {index}.",
        #context_template="I am {index} that I can keep my feelings under control.",
        context_template="I feel {index} about my ability to keep my feelings under control.",
        answer_template="This is {frequency} correct.",
        dimensions={
            "frequency":frequency_weights,
            "index":self.dict_attitude,
        },
        descriptor = {"Questionnair":"SOC",
                      "Factor":"Manageability",
                      "Ordinal":29,
                      "Original":"How often do you have feelings that you're not sure you can keep under control? "
        },
        **kwargs,
    )

soc_qmnli_list = [SOCQ4, SOCQ5, SOCQ6, SOCQ8, SOCQ9, SOCQ12, SOCQ16, SOCQ19, SOCQ21, SOCQ25, SOCQ26, SOCQ28, SOCQ29]



"""
Summary of Changes Made to SOC Questionnaire

SOCQ4:
    - Fixed preposition: "What goes around me" → "What goes on around me"

SOCQ12:
    - Fixed article/number: "In unfamiliar situation" → "In unfamiliar situations"
"""
