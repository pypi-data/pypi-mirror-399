# -*- coding: utf-8 -*-

# Define here the models for your scraped items

from scrapy import Item, Field


class RawResponseItem(Item):
    appid = Field()
    crawlid = Field()
    url = Field()
    responseUrl = Field()
    statusCode = Field()
    success = Field()
    exception = Field()
    encoding = Field()
    attrs = Field()


class MenuResponseItem(RawResponseItem):
    playgroundId = Field()
    groupCategoryName = Field()
    groupName = Field()
    groupUrl = Field()


class ScreenshotResponseItem(RawResponseItem):
    productUrl = Field()
    price = Field()
    priceDatetime = Field()


class ProductResponseItem(RawResponseItem):
    playgroundId = Field()
    productUrl = Field()
    groupId = Field()
    price = Field()


class AggregatorPriceResponseItem(RawResponseItem):
    aggregatorUrl = Field()
    playgroundName = Field()
    playgroundHost = Field()
    price = Field()


class ProductDetailsResponseItem(RawResponseItem):
    playgroundId = Field()
    productUrl = Field()
    groupId = Field()
    imageUrls = Field()
    type = Field()
    name = Field()
    brandName = Field()
    sellerName = Field()
    description = Field()
    details = Field()
    comments = Field()


class ReviewResponseItem(RawResponseItem):
    technoBlogId = Field()
    reviewUrl = Field()
    createDate = Field()
    name = Field()
    category = Field()
    imageUrl = Field()


class ReviewDetailsResponseItem(ReviewResponseItem):
    author = Field()
    keywords = Field()
    description = Field()
    pros = Field()
    cons = Field()
    productName = Field()
    productParameters = Field()
    verdict = Field()
    comments = Field()
    baseParameters = Field()


class NewsDetailsResponseItem(RawResponseItem):
    technoBlogId = Field()
    newsUrl = Field()
    createDate = Field()
    category = Field()
    author = Field()
    name = Field()
    description = Field()
    imageUrl = Field()
    keywords = Field()
    views = Field()
    reactions = Field()


class BrandProductResponseItem(RawResponseItem):
    brandId = Field()
    groupId = Field()
    productUrl = Field()
    code = Field()
    name = Field()
    imageUrls = Field()
    minPrice = Field()


class BrandProductDetailsResponseItem(BrandProductResponseItem):
    description = Field()
    variations = Field()
    productParameters = Field()


class TourResponseItem(RawResponseItem):
    operatorId = Field()
    adult = Field()
    child = Field()
    startDate = Field()
    nights = Field()
    hotelName = Field()
    hotelUrl = Field()
    roomType = Field()
    mealCode = Field()
    flightCodeThere = Field()
    flightClassThere = Field()
    flightCodeBack = Field()
    flightClassBack = Field()
    insurance = Field()
    price = Field()


class HotelResponseItem(RawResponseItem):
    operatorId = Field()
    name = Field()
    description = Field()
    site = Field()
    photos = Field()
    regionId = Field()
    latitude = Field()
    longitude = Field()
    address = Field()
    stars = Field()
    rating = Field()
    foundationYear = Field()
    renovationYear = Field()
    totalArea = Field()
    seaDistance = Field()
    airportDistance = Field()
    features = Field()
