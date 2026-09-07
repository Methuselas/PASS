# Ranking

1. Prefer `this->` for a single dependent-base member access. It enables lookup
   while preserving virtual dispatch and keeps the dependency visible at the
   call.
2. Prefer a `using` declaration when several calls should share an unqualified
   inherited name. It preserves virtual dispatch but affects the whole derived
   scope.
3. Use explicit base qualification only when deliberately selecting that base
   implementation. It suppresses virtual dispatch, so it is the wrong default
   for a virtual customization point.
