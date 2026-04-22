from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import Transaction, Category, SaldoAwal
from .forms import TransactionForm, CategoryForm, SaldoAwalForm

# ============================================================
# DASHBOARD - TRANSAKSI UTAMA
# ============================================================
@login_required
def transaction_list(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)  # KIRIM USER KE FORM
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(request.user)  # KIRIM USER KE FORM

    # AMBIL SEMUA TRANSAKSI MILIK USER
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # HITUNG TOTAL KESELURUHAN
    total_income = transactions.filter(type='IN').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='OUT').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # REKAP PER BULAN
    rekap_month = (
        Transaction.objects.filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month', 'type')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )

    # UBAH QUERY MENJADI DICTIONARY
    rekap = {}
    for item in rekap_month:
        month = item['month'].strftime('%B %Y')
        if month not in rekap:
            rekap[month] = {'income': 0, 'expense': 0}
        if item['type'] == 'IN':
            rekap[month]['income'] = item['total']
        else:
            rekap[month]['expense'] = item['total']

    # HITUNG BALANCE PER BULAN
    for month in rekap:
        rekap[month]['balance'] = rekap[month]['income'] - rekap[month]['expense']

    context = {
        'transactions': transactions,
        'form': form,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'rekap': rekap,
    }
    return render(request, 'tracker/transaction_list.html', context)


# ============================================================
# EDIT TRANSAKSI
# ============================================================
@login_required
def edit_transaction(request, pk):
    # AMBIL TRANSAKSI MILIK USER BERDASARKAN ID, JIKA TIDAK ADA TAMPILKAN 404
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(request.user, instance=transaction)  # TAMPILKAN DATA LAMA

    return render(request, 'tracker/edit_transaction.html', {'form': form})


# ============================================================
# DELETE TRANSAKSI
# ============================================================
@login_required
def delete_transaction(request, pk):
    # AMBIL TRANSAKSI MILIK USER BERDASARKAN ID
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')

    return render(request, 'tracker/delete_transaction.html', {'transaction': transaction})


# ============================================================
# KATEGORI - LIST & ADD
# ============================================================
@login_required
def category_list(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user  # SET USER
            category.save()
            return redirect('category_list')
    else:
        form = CategoryForm()

    # PISAHKAN KATEGORI PEMASUKAN DAN PENGELUARAN
    categories_in = Category.objects.filter(user=request.user, type='IN')
    categories_out = Category.objects.filter(user=request.user, type='OUT')

    context = {
        'form': form,
        'categories_in': categories_in,
        'categories_out': categories_out,
    }
    return render(request, 'tracker/category_list.html', context)


# ============================================================
# EDIT KATEGORI
# ============================================================
@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)  # TAMPILKAN DATA LAMA

    return render(request, 'tracker/edit_category.html', {'form': form})


# ============================================================
# DELETE KATEGORI
# ============================================================
@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        category.delete()
        return redirect('category_list')

    return render(request, 'tracker/delete_category.html', {'category': category})


# ============================================================
# SALDO AWAL
# ============================================================
@login_required
def saldo_awal(request):
    if request.method == 'POST':
        form = SaldoAwalForm(request.POST)
        if form.is_valid():
            saldo = form.save(commit=False)
            saldo.user = request.user  # SET USER
            saldo.save()
            return redirect('transaction_list')
    else:
        form = SaldoAwalForm()

    # AMBIL SEMUA SALDO AWAL MILIK USER
    saldo_list = SaldoAwal.objects.filter(user=request.user)

    context = {
        'form': form,
        'saldo_list': saldo_list,
    }
    return render(request, 'tracker/saldo_awal.html', context)


# ============================================================
# LAPORAN BULANAN
# ============================================================
@login_required
def laporan(request):
    transactions = Transaction.objects.filter(user=request.user)

    # REKAP PER BULAN DAN KATEGORI - pisah annotate dan values
    rekap_month = (
        transactions
        .values('date', 'type', 'category__name', 'amount')  # AMBIL DATA DULU
        .order_by('-date', 'type')
    )

    # UBAH QUERY MENJADI DICTIONARY PER BULAN
    laporan_data = {}
    for item in rekap_month:
        month = item['date'].strftime('%B %Y')  # FORMAT BULAN DARI DATE
        if month not in laporan_data:
            laporan_data[month] = {'income': {}, 'expense': {}, 'total_income': 0, 'total_expense': 0}

        category_name = item['category__name'] or 'Without Category'
        amount = item['amount']

        if item['type'] == 'IN':
            # TAMBAHKAN KE KATEGORI YANG SAMA JIKA SUDAH ADA
            if category_name in laporan_data[month]['income']:
                laporan_data[month]['income'][category_name] += amount
            else:
                laporan_data[month]['income'][category_name] = amount
            laporan_data[month]['total_income'] += amount
        else:
            if category_name in laporan_data[month]['expense']:
                laporan_data[month]['expense'][category_name] += amount
            else:
                laporan_data[month]['expense'][category_name] = amount
            laporan_data[month]['total_expense'] += amount

    # HITUNG BALANCE PER BULAN + SALDO AWAL
    for month in laporan_data:
        month_date = datetime.strptime(month, '%B %Y')
        saldo = SaldoAwal.objects.filter(
            user=request.user,
            month__year=month_date.year,
            month__month=month_date.month
        ).first()

        laporan_data[month]['saldo_awal'] = saldo.amount if saldo else 0
        laporan_data[month]['balance'] = (
            laporan_data[month]['saldo_awal'] +
            laporan_data[month]['total_income'] -
            laporan_data[month]['total_expense']
        )

    context = {'laporan': laporan_data}
    return render(request, 'tracker/laporan.html', context)


# ============================================================
# RESET DATA
# ============================================================
@login_required
def reset_data(request):
    # HAPUS SEMUA TRANSAKSI MILIK USER YANG SEDANG LOGIN
    Transaction.objects.filter(user=request.user).delete()
    return redirect('transaction_list')