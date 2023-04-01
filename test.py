from CommonHelper import *

print(get_rough_token_len("Hello world!"))
print(get_rough_token_len("如果不用发票报销，"))
print(get_rough_token_len("如果不用发票报销，可以使用支付证明作为报销凭证，但应尽量避免使用。"))
REFINE_DEFAULT_REFINE_PROMPT_TMPL = (
    "The original question is as follows: \n"
    "We have provided an existing answer: \n"
    "We have the opportunity to refine the existing answer"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "66666\n"
    "------------\n"
    "Given the new context, refine the original answer to better "
    "answer the question."
    "If the context isn't useful, return the original answer."
)

print(REFINE_DEFAULT_REFINE_PROMPT_TMPL)
