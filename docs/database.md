# Banco de dados

SQLite com schema gerenciado por migrations Django.

Relações principais: Customer 1:N Vehicle; Vehicle 1:N ServiceOrder; ServiceOrder 1:N Damage, ServicePart e StatusHistory; DamageCategory 1:N Damage e CauseSuggestion; Part 1:N ServicePart.

Clientes, veículos, peças e usuários históricos são desativados. Ordens usam `PROTECT` para preservar autoria e relacionamentos. Placa e número público da ordem são únicos. A numeração segue `BB-AAAA-NNNN`.
