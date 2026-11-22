# Pilot planı

<!-- İçeriğin geri kalanı sonraki görevde yazılacak. Aşama 0 yalnız başlığı
     açıyor ve aşağıdaki eşzamanlılık kısıtını kaydediyor. -->

## Eşzamanlılık kısıtı

AppWorld motoru ajan sürecinden ayrı bir süreç olarak koşabiliyor.
Komutları `appworld serve environment` ve `appworld serve apis`. Ancak **bir
sunucu süreci aynı anda yalnız tek bir dünya tutuyor.** Birinci dünya etkinken
ikincisini başlatmaya çalışmak HTTP 400 döndürüyor:

```
The active task world is X. But you have requested to operate on Y
```

Sebebi iki katlı. Freezegun zamanı süreç geneli taklit ediyor, ayrıca
veritabanı bağlantılarının sızmaması isteniyor.

**Sonucu.** Paralel epizot, port başına ayrı sunucu süreci gerektiriyor. Pilot
planı bunu bir bellek ve çekirdek bütçesi kalemi olarak taşımak zorunda: N
paralel epizot, N motor süreci demek.
