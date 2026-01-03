# SPDX-FileCopyrightText: 2025 Michael Pöhn <michael@poehn.at>
# SPDX-License-Identifier: MIT

"""Data Type definitions/models for Funding JSON."""

from enum import Enum
from typing import Optional, Any, List, TypeVar, Type, cast, Callable


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_str(x: Any) -> str:
    """Convert x to str."""
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    """Convert x to None."""
    assert x is None
    return x


def from_union(fs, x):
    """Iterate over the type conversion functions in fs and return the value of the first successful conversion."""
    for f in fs:
        try:
            return f(x)
        except AssertionError:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    """Try to convert any given value x to enum value of enum-type c."""
    assert isinstance(x, c)
    return x.value


def to_class(c: Type[T], x: Any) -> dict:
    """Convert value x to a dictonary with the structure of type c."""
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_float(x: Any) -> float:
    """Convert value x from json dictionary to python float."""
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_int(x: Any) -> int:
    """Convert value x from json dictonary to python int."""
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_float(x: Any) -> float:
    """Convert x to json dictionary float."""
    assert isinstance(x, (int, float))
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    """Convert to typed list."""
    assert isinstance(x, list)
    return [f(y) for y in x]


class Url:
    """URLs with back-link verification support."""

    url: str
    """URL for storing web links."""

    well_known: Optional[str]
    """Required if the above url and the URL of the funding.json manifest do not have the same
    hostname. This url should have the same hostname as the url to verify that the publisher
    of the manifest is authorised to solicit funding on behalf of the url. The url should end
    with /.well-known/funding-manifest-urls.
    """

    def __init__(self, url: str, well_known: Optional[str]) -> None:
        """Create new instance."""
        self.url = url
        self.well_known = well_known

    @staticmethod
    def from_dict(obj: Any) -> "Url":
        """Convert data into Url object."""
        assert isinstance(obj, dict)
        url = from_str(obj.get("url"))
        well_known = from_union([from_str, from_none], obj.get("wellKnown"))
        return Url(url, well_known)

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["url"] = from_str(self.url)
        if self.well_known is not None:
            result["wellKnown"] = from_union([from_str, from_none], self.well_known)
        return result


class Role(Enum):
    """Role in relation to the entity. [owner, steward, maintainer, contributor, other]. Use the closest approximation."""

    CONTRIBUTOR = "contributor"
    MAINTAINER = "maintainer"
    OTHER = "other"
    OWNER = "owner"
    STEWARD = "steward"


class EntityType(Enum):
    """Type of the entity. [individual, group, organisation, other], Use the closest approximation."""

    GROUP = "group"
    INDIVIDUAL = "individual"
    ORGANISATION = "organisation"
    OTHER = "other"


class Entity:
    """The entity associated with the project, soliciting funds."""

    description: str
    """Information about the entity."""

    email: str
    """Contact email."""

    name: str
    """Name of the entity."""

    phone: Optional[str]
    """Contact phone number. Generally suitable for organisations."""

    role: Role
    """Role in relation to the entity. [owner, steward, maintainer, contributor, other]. Use the
    closest approximation.
    """
    type: EntityType
    """Type of the entity. [individual, group, organisation, other], Use the closest
    approximation.
    """
    webpage_url: Url
    """Webpage with information about the entity."""

    def __init__(
        self,
        description: str,
        email: str,
        name: str,
        phone: Optional[str],
        role: Role,
        type: EntityType,
        webpage_url: Url,
    ) -> None:
        """Create new instance."""
        self.description = description
        self.email = email
        self.name = name
        self.phone = phone
        self.role = role
        self.type = type
        self.webpage_url = webpage_url

    @staticmethod
    def from_dict(obj: Any) -> "Entity":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        email = from_str(obj.get("email"))
        name = from_str(obj.get("name"))
        phone = from_union([from_str, from_none], obj.get("phone"))
        role = Role(obj.get("role"))
        type = EntityType(obj.get("type"))
        webpage_url = Url.from_dict(obj.get("webpageUrl"))
        return Entity(description, email, name, phone, role, type, webpage_url)

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["description"] = from_str(self.description)
        result["email"] = from_str(self.email)
        result["name"] = from_str(self.name)
        if self.phone is not None:
            result["phone"] = from_union([from_str, from_none], self.phone)
        result["role"] = to_enum(Role, self.role)
        result["type"] = to_enum(EntityType, self.type)
        result["webpageUrl"] = to_class(Url, self.webpage_url)
        return result


class ChannelType(Enum):
    """Type of the channel. [bank, payment-provider, cheque, cash, other]."""

    BANK = "bank"
    CASH = "cash"
    CHEQUE = "cheque"
    OTHER = "other"
    PAYMENT_PROVIDER = "payment-provider"


class Channel:
    """Funding Channels as defiending by https://fundingjson.org."""

    address: Optional[str]
    """A short unstructured textual representation of the payment address for the channel. eg:
    "Account: 12345 (branch: ABCX)", "mypaypal@domain.com", "https://payment-url.com", or a
    physical address for cheques.
    """
    description: Optional[str]
    """Any additional description or instructions for the payment channel."""

    guid: str
    """A short unique ID for the channel. Lowercase-alphanumeric-dashes only. eg: mybank,
    my-paypal.
    """
    type: ChannelType
    """Type of the channel. [bank, payment-provider, cheque, cash, other]."""

    def __init__(
        self,
        address: Optional[str],
        description: Optional[str],
        guid: str,
        type: ChannelType,
    ) -> None:
        """Create new instance."""
        self.address = address
        self.description = description
        self.guid = guid
        self.type = type

    @staticmethod
    def from_dict(obj: Any) -> "Channel":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        address = from_union([from_str, from_none], obj.get("address"))
        description = from_union([from_str, from_none], obj.get("description"))
        guid = from_str(obj.get("guid"))
        type = ChannelType(obj.get("type"))
        return Channel(address, description, guid, type)

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        if self.address is not None:
            result["address"] = from_union([from_str, from_none], self.address)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        result["guid"] = from_str(self.guid)
        result["type"] = to_enum(ChannelType, self.type)
        return result


class History:
    """Funding histroy as specified by https://fundingjson.org."""

    currency: str
    """Three letter ISO 4217 currency code. eg: USD, EUR."""

    description: Optional[str]
    """Any additional description."""

    expenses: Optional[float]
    """Expenses for the year."""

    income: Optional[float]
    """Income for the year."""

    taxes: Optional[float]
    """Taxes for the year."""

    year: int
    """Year (fiscal, preferably)."""

    def __init__(
        self,
        currency: str,
        description: Optional[str],
        expenses: Optional[float],
        income: Optional[float],
        taxes: Optional[float],
        year: int,
    ) -> None:
        """Create new instance."""
        self.currency = currency
        self.description = description
        self.expenses = expenses
        self.income = income
        self.taxes = taxes
        self.year = year

    @staticmethod
    def from_dict(obj: Any) -> "History":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        currency = from_str(obj.get("currency"))
        description = from_union([from_str, from_none], obj.get("description"))
        expenses = from_union([from_float, from_none], obj.get("expenses"))
        income = from_union([from_float, from_none], obj.get("income"))
        taxes = from_union([from_float, from_none], obj.get("taxes"))
        year = from_int(obj.get("year"))
        return History(currency, description, expenses, income, taxes, year)

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["currency"] = from_str(self.currency)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        if self.expenses is not None:
            result["expenses"] = from_union([to_float, from_none], self.expenses)
        if self.income is not None:
            result["income"] = from_union([to_float, from_none], self.income)
        if self.taxes is not None:
            result["taxes"] = from_union([to_float, from_none], self.taxes)
        result["year"] = from_int(self.year)
        return result


class Frequency(Enum):
    """Frequency of the funding. [one-time, weekly, fortnightly, monthly, yearly, other]."""

    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"
    ONE_TIME = "one-time"
    OTHER = "other"
    WEEKLY = "weekly"
    YEARLY = "yearly"


class Status(Enum):
    """Indicates whether this plan is currently active or inactive. [active, inactive]."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class Plan:
    """Funding plan as specified by https://fundingjson.org."""

    amount: float
    """The solicited amount for this plan. 0 is a wildcard that indicates "any amount"."""

    channels: List[str]
    """One or more channel IDs defined in channels[] via which this plan can accept payments"""

    currency: str
    """Three letter ISO 4217 currency code. eg: USD, EUR."""

    description: Optional[str]
    """Any additional description or instructions for the funding plan."""

    frequency: Frequency
    """Frequency of the funding. [one-time, weekly, fortnightly, monthly, yearly, other]"""

    guid: str
    """A short unique ID for the plan. Lowercase-alphanumeric-dashes only. eg: mybank, paypal."""

    name: str
    """Name of the funding plan. eg: "Starter support plan", "Infra hosting", "Monthly funding
    plan".
    """
    status: Status
    """Indicates whether this plan is currently active or inactive. [active, inactive]."""

    def __init__(
        self,
        amount: float,
        channels: List[str],
        currency: str,
        description: Optional[str],
        frequency: Frequency,
        guid: str,
        name: str,
        status: Status,
    ) -> None:
        """Create new instance."""
        self.amount = amount
        self.channels = channels
        self.currency = currency
        self.description = description
        self.frequency = frequency
        self.guid = guid
        self.name = name
        self.status = status

    @staticmethod
    def from_dict(obj: Any) -> "Plan":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        amount = from_float(obj.get("amount"))
        channels = from_list(from_str, obj.get("channels"))
        currency = from_str(obj.get("currency"))
        description = from_union([from_str, from_none], obj.get("description"))
        frequency = Frequency(obj.get("frequency"))
        guid = from_str(obj.get("guid"))
        name = from_str(obj.get("name"))
        status = Status(obj.get("status"))
        return Plan(
            amount, channels, currency, description, frequency, guid, name, status
        )

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["amount"] = to_float(self.amount)
        result["channels"] = from_list(from_str, self.channels)
        result["currency"] = from_str(self.currency)
        if self.description is not None:
            result["description"] = from_union([from_str, from_none], self.description)
        result["frequency"] = to_enum(Frequency, self.frequency)
        result["guid"] = from_str(self.guid)
        result["name"] = from_str(self.name)
        result["status"] = to_enum(Status, self.status)
        return result


class Funding:
    """This describes one or more channels via which the entity can receive funds."""

    channels: List[Channel]
    history: Optional[List[History]]
    """A simple summary of funding history. Only include if at least one, either income or
    expenses, have to be communicated.
    """
    plans: List[Plan]

    def __init__(
        self,
        channels: List[Channel],
        history: Optional[List[History]],
        plans: List[Plan],
    ) -> None:
        """Create new instance."""
        self.channels = channels
        self.history = history
        self.plans = plans

    @staticmethod
    def from_dict(obj: Any) -> "Funding":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        channels = from_list(Channel.from_dict, obj.get("channels"))
        history = from_union(
            [lambda x: from_list(History.from_dict, x), from_none], obj.get("history")
        )
        plans = from_list(Plan.from_dict, obj.get("plans"))
        return Funding(channels, history, plans)

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["channels"] = from_list(lambda x: to_class(Channel, x), self.channels)
        if self.history is not None:
            result["history"] = from_union(
                [lambda x: from_list(lambda x: to_class(History, x), x), from_none],
                self.history,
            )
        result["plans"] = from_list(lambda x: to_class(Plan, x), self.plans)
        return result


class Project:
    """One or more projects for which the funding is solicited."""

    description: str
    """Description of the project."""
    guid: str
    """A short unique ID for the project. Lowercase-alphanumeric-dashes only. eg:
    my-cool-project.
    """
    licenses: List[str]
    """The project's licenses (up to 5). For standard licenses, use the license ID from the SDPX
    index prefixed by "spdx:". eg: "spdx:GPL-3.0", "spdx:CC-BY-SA-4.0".
    """
    name: str
    """Name of the project."""
    repository_url: Url
    """URL of the repository where the project's source code and other assets are available."""
    tags: List[str]
    """Up to 10 general tags describing the project. For reference, see
    https://floss.fund/static/project-tags.txt.
    """
    webpage_url: Url
    """Webpage with information about the project."""

    def __init__(
        self,
        description: str,
        guid: str,
        licenses: List[str],
        name: str,
        repository_url: Url,
        tags: List[str],
        webpage_url: Url,
    ) -> None:
        """Create new instance."""
        self.description = description
        self.guid = guid
        self.licenses = licenses
        self.name = name
        self.repository_url = repository_url
        self.tags = tags
        self.webpage_url = webpage_url

    @staticmethod
    def from_dict(obj: Any) -> "Project":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        guid = from_str(obj.get("guid"))
        licenses = from_list(from_str, obj.get("licenses"))
        name = from_str(obj.get("name"))
        repository_url = Url.from_dict(obj.get("repositoryUrl"))
        tags = from_list(from_str, obj.get("tags"))
        webpage_url = Url.from_dict(obj.get("webpageUrl"))
        return Project(
            description, guid, licenses, name, repository_url, tags, webpage_url
        )

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["description"] = from_str(self.description)
        result["guid"] = from_str(self.guid)
        result["licenses"] = from_list(from_str, self.licenses)
        result["name"] = from_str(self.name)
        result["repositoryUrl"] = to_class(Url, self.repository_url)
        result["tags"] = from_list(from_str, self.tags)
        result["webpageUrl"] = to_class(Url, self.webpage_url)
        return result


class Manifest:
    """Funding JSON Manifest data class."""

    entity: Entity
    """The entity associated with the project, soliciting funds."""

    funding: Funding
    """This describes one or more channels via which the entity can receive funds."""

    projects: Optional[List[Project]]
    version: Optional[str]
    """Manifest content version"""

    def __init__(
        self,
        entity: Entity,
        funding: Funding,
        projects: Optional[List[Project]],
        version: Optional[str],
    ) -> None:
        """Create new instance."""
        self.entity = entity
        self.funding = funding
        self.projects = projects
        self.version = version

    @staticmethod
    def from_dict(obj: Any) -> "Manifest":
        """Convert data into DTO."""
        assert isinstance(obj, dict)
        entity = Entity.from_dict(obj.get("entity"))
        funding = Funding.from_dict(obj.get("funding"))
        projects = from_union(
            [lambda x: from_list(Project.from_dict, x), from_none], obj.get("projects")
        )
        version = from_union([from_str, from_none], obj.get("version"))
        return Manifest(entity, funding, projects, version)

    def to_dict(self) -> dict:
        """Convert data in this object to dictionary."""
        result: dict = {}
        result["entity"] = to_class(Entity, self.entity)
        result["funding"] = to_class(Funding, self.funding)
        if self.projects is not None:
            result["projects"] = from_union(
                [lambda x: from_list(lambda x: to_class(Project, x), x), from_none],
                self.projects,
            )
        if self.version is not None:
            result["version"] = from_union([from_str, from_none], self.version)
        return result
