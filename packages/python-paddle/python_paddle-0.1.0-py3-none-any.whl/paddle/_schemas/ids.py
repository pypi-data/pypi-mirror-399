from typing import Annotated

from pydantic import Field


AddressID = Annotated[str, Field(pattern="^add_")]
BusinessID = Annotated[str, Field(pattern="^biz_")]
CustomerID = Annotated[str, Field(pattern="^ctm_")]
DiscountID = Annotated[str, Field(pattern="^dsc_")]
PriceID = Annotated[str, Field(pattern="^pri_")]
ProductID = Annotated[str, Field(pattern="^pro_")]
SubscriptionID = Annotated[str, Field(pattern="^sub_")]
TransactionID = Annotated[str, Field(pattern="^txn_")]
