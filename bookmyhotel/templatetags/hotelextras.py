from django import template

from math import floor, ceil

register = template.Library()

@register.filter(name='stars')
def stars(value):
    if value:
        full_stars = floor(value)
        half_star = ceil(value) > full_stars
        empty_stars = 5 - ceil(value)

        return '<i class="ri-star-fill"></i>' * full_stars + '<i class="ri-star-half-line"></i>' * half_star + '<i class="ri-star-line"></i>' * empty_stars
    else:
        return '<i class="ri-star-line"></i>' * 5

