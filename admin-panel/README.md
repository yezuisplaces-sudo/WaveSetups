# WaveSetups Admin Panel

Bu panel ile `.mdx` sayfalarını ve `docs.json` ayarlarını web arayüzünden düzenleyebilirsin.

## 1) Kurulum

```bash
cd "C:\Users\Yusuf Ali Kaya\Documents\New project\wavesetups-docs"
python -m pip install -r admin-panel\requirements.txt
```

## 2) Şifreyi Belirle (önerilir)

PowerShell:

```powershell
$env:WAVE_ADMIN_PASSWORD="buraya-guclu-bir-sifre-yaz"
```

Opsiyonel session secret:

```powershell
$env:WAVE_ADMIN_SECRET="uzun-rastgele-secret"
```

## 3) Paneli Çalıştır

```bash
python admin-panel\app.py
```

Panel adresi:

`http://127.0.0.1:5050`

## 4) Dokümantasyonu Yayın Öncesi Kontrol

```bash
npm run mint:check
```

## Not

Bu panel varsayılan olarak lokal kullanım içindir. Public internete açmadan önce ters proxy, HTTPS ve ek güvenlik katmanları eklenmelidir.

## Özellikler

- Çok daha hızlı dosya listesi (yalnızca içerik klasörleri taranır).
- Panelden yeni sayfa oluşturma:
  - Kategori seç (`Pluginler`, `Plugin Paketleri`, `Ana Sayfa`)
  - Başlık gir
  - Sistem otomatik `.mdx` dosyası üretir
  - `docs.json` menüsüne otomatik ekler
