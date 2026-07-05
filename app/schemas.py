from pydantic import BaseModel, Field

class WeatherResponse(BaseModel):
    city: str = Field(max_length=30)
    weather: str = Field(max_length=30)
    temperature: float= Field(ge=-90.0)
    feels_temperature: float= Field(le=200.0)