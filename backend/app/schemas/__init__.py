from .auth import UserCreate, UserLogin, Token, UserResponse
from .client import ClientCreate, ClientUpdate, ClientResponse
from .mechanic import MechanicCreate, MechanicUpdate, MechanicResponse
from .order import OrderCreate, OrderUpdate, OrderResponse, OrderItemAdd, OrderStatusUpdate, OrderStatusResponse
from .car import CarCreate, CarUpdate, CarResponse
from .post import PostCreate, PostUpdate, PostResponse, PostOccupyRequest
from .work import WorkCreate, WorkUpdate, WorkResponse
from .part import PartCreate, PartUpdate, PartResponse
from .report import RevenueReportRequest, DailyRevenue, RevenueReportResponse, PopularWork, PopularWorksResponse, MechanicLoad, MechanicsLoadResponse, SummaryReportResponse