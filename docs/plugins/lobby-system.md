# Lobby System

Lobby System, oyuncularin ilk giris deneyimini gelistirmek icin tasarlanmistir.

## Ozellikler

- Join item sistemi
- Otomatik scorebord
- NPC tabanli sunucu yonlendirme
- Cift dil mesaj destegi

## Kurulum

1. Plugin dosyasini `plugins/` klasorune atin.
2. `/ls setup` komutunu calistirin.
3. NPC ve item aksiyonlarini config dosyasindan ayarlayin.

## Komutlar

| Komut | Aciklama | Yetki |
| --- | --- | --- |
| `/ls setup` | Ilk kurulum sihirbazini acar | Admin |
| `/ls reload` | Config dosyalarini yeniler | Admin |
| `/hub` | Lobiye doner | Oyuncu |

## Permission Node'lari

```txt
wavesetups.lobby.hub
wavesetups.lobby.setup
wavesetups.lobby.reload
```
