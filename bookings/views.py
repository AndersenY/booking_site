from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404
from .models import Apartment
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.utils.dateparse import parse_date
import re
from decimal import Decimal
from bookings.models import Apartment, Calendar
from django.shortcuts import render, redirect
from .forms import BookingForm
import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Ошибка при подключении: {response.status_code}")
        return None


def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    for post in soup.find_all('div', class_='d-post'):
        img_tag = post.find('img', attrs={'data-lazy': True})
        img_url = img_tag['data-lazy'] if img_tag else None

        desc_tag = post.find('div', class_='d-post_desc')
        description = desc_tag.text.strip() if desc_tag else None

        price_tag = post.find('div', class_='d-post_price')
        price_str = price_tag.text.strip() if price_tag else None

        # Преобразование строки цены в Decimal
        if price_str:
            price_str = re.sub(r'[^\d]', '', price_str)
            price = Decimal(price_str) if price_str else None
        else:
            price = None

        # Отладочные сообщения

        link_tag = post.find('a', class_='d-post_link')
        link_url = link_tag['href'] if link_tag else '#'
        full_link_url = f'https://doska.ykt.ru{link_url}'

        # Проверка: если цена отсутствует, пропускаем добавление
        if price is None:
            print(
                f"Price is None for the apartment with link: {full_link_url}. Skipping this entry.")
            continue

        # Всегда добавляем в items для отображения
        items.append({
            'image': img_url,
            'description': description,
            'price': price,
            'link': full_link_url,
            'id': get_object_or_404(Apartment, link=full_link_url).id
        })

        # Проверка: если квартира с таким же link уже есть в базе, не добавляем её
        if not Apartment.objects.filter(link=full_link_url).exists():
            # Создаем экземпляр Calendar для новой квартиры
            calendar = Calendar.objects.create()  # Создаем пустой календарь

            apartment = Apartment(
                image=img_url,
                description=description,
                price_per_night=price,
                link=full_link_url,
                calendar=calendar  # Связываем с новым календарем
            )
            apartment.save()
            print(f"Apartment added with link: {full_link_url}")

        print(f"Total items parsed: {len(items)}")

    return items


def home(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = BookingForm()

    # Получение данных о квартирах

    url = 'https://doska.ykt.ru/nedvizhimost/kvartiry/sdau_v_posutochnuu_arendu'
    html_content = fetch_page(url)

    items = []
    if html_content:
        items = parse_data(html_content)

    # Добавляем проверку, если нет квартир
    if not items:
        print("No apartments found.")
        # Можно также передать сообщение в шаблон, если нужно отобразить на странице
        return render(request, 'home.html', {
            'form': form,
            'items': items,
            'error': 'Квартиры не найдены.'  # Передаем сообщение об ошибке
        })

    return render(request, 'home.html', {'form': form, 'items': items})


def search_apartments(request):
    check_in_date_str = request.GET.get('check_in_date')
    check_out_date_str = request.GET.get('check_out_date')
    guests = request.GET.get('guests')

    # Получаем сегодняшнюю дату
    today = timezone.now().date()

    print(today)

    # Преобразование строковых дат в объекты даты
    check_in_date = parse_date(
        check_in_date_str) if check_in_date_str else None
    check_out_date = parse_date(
        check_out_date_str) if check_out_date_str else None

    print(check_in_date)
    print(check_out_date)

    print(bool(check_in_date > check_out_date))

    # Проверка, что даты не позже сегодняшнего дня
    if check_in_date and check_in_date < today:
        return render(request, 'search_results.html', {'error': 'Дата заезда не может быть раньше сегодняшнего дня.'})

    if check_out_date and check_out_date < today:
        return render(request, 'search_results.html', {'error': 'Дата выезда не может быть позже сегодняшнего дня.'})

    # Проверка, что дата заезда не позже даты выезда
    if check_in_date and check_out_date and check_in_date >= check_out_date:
        return render(request, 'search_results.html', {'error': 'Дата заезда не может быть позже даты выезда.'})

    # Поиск доступных квартир
    available_apartments = Apartment.objects.all()

    if check_in_date and check_out_date and guests:
        # Получаем все даты в диапазоне от check_in_date до check_out_date
        date_range = [check_in_date + timedelta(days=i)
                      for i in range((check_out_date - check_in_date).days + 1)]

        print(date_range)

        available_apartments_list = []

        for apartment in available_apartments:
            # Получаем забронированные даты из календаря
            booked_dates = apartment.calendar.booked_dates if apartment.calendar else []

            print(booked_dates)

            # Проверяем, пересекаются ли запрашиваемые даты с забронированными
            if not any(date in booked_dates for date in [date.isoformat() for date in date_range]):
                # Если пересечений нет, добавляем квартиру в доступные
                available_apartments_list.append(apartment)

    return render(request, 'search_results.html', {'apartments': available_apartments_list})


def apartment_detail(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    print(apartment.calendar)

    return render(request, 'apartment_detail.html', {
        'apartment': apartment
    })
