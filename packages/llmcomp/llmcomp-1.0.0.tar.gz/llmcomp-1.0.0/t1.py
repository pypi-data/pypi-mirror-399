from llmcomp import Question

MODELS = {
    "gpt-5": ["gpt-5"],
}

# Requires OPENAI_API_KEY env variable
question = Question.create(
    type="free_form",
    paraphrases=["Name a pretty song. Answer with the name only."],
    samples_per_paraphrase=100,
    temperature=1,
)
question.plot(MODELS, min_fraction=0.03)
df = question.df(MODELS)
print(df.head(1).iloc[0])