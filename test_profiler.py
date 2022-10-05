import yappi
import user_filters
import db


with yappi.run(builtins=True):
    conn = db.Connection()
    _filter = user_filters.Category
    ads = conn.get_ads()
    ads = _filter.apply(conn, 536303432, ads)
    print(len(ads))


print("================ Func Stats ===================")

yappi.get_func_stats().print_all()

print("\n================ Thread Stats ===================")

yappi.get_thread_stats().print_all()


print("\nYappi Backend Types   : ",yappi.BACKEND_TYPES)
print("Yappi Clock Types     : ", yappi.CLOCK_TYPES)
print("Yappi Stats Columns   : ", yappi.COLUMNS_FUNCSTATS)
print("Yappi Line Sep        : ", yappi.LINESEP)

