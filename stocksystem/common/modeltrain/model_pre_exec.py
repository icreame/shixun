from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import Trainer, TrainingArguments
model = AutoModelForSequenceClassification.from_pretrained('本地模型路径')
tokenizer = AutoTokenizer.from_pretrained('本地模型路径')

inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")



training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    logging_dir='./logs',
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
)

trainer.train()