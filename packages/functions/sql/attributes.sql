    -- Gieo mầm cho bảng attributes V2 (đã cập nhật)
    INSERT INTO attributes (type, name, slug, possible_values) VALUES
    -- Tiện ích chung (Boolean)
    ('boolean', 'Điều hoà', 'air_conditioner', NULL),
    ('boolean', 'Nóng lạnh', 'water_heater', NULL),
    ('boolean', 'Thang máy', 'elevator', NULL),
    ('boolean', 'Khoá vân tay', 'fingerprint_lock', NULL),
    ('boolean', 'Cho phép vật nuôi', 'allows_pets', NULL),
    ('boolean', 'Chung chủ', 'owner_occupied', NULL),

-- Chính sách & Quy định (Enum)
    ('enum', 'Đối tượng cho thuê', 'guest_policy', ARRAY['female_only', 'male_only', 'any']),
    ('enum', 'Giờ giấc', 'access_hours', ARRAY['free', 'restricted']),
    ('enum', 'Loại bếp', 'kitchen_type', ARRAY['private', 'shared']),
    ('enum', 'Loại vệ sinh', 'bathroom_type', ARRAY['private', 'shared']),

-- Thông số số lượng (Integer)
    ('integer', 'Số người chung bếp', 'kitchen_sharers_count', NULL),
    ('integer', 'Số người chung vệ sinh', 'bathroom_sharers_count', NULL),
    ('integer', 'Số người hiện tại', 'current_occupants', NULL),
    ('integer', 'Cần tìm thêm người', 'needed_occupants', NULL),
    ('integer', 'Ở tối đa', 'max_occupants', NULL),
    ('integer', 'Số xe tối đa', 'parking_limit', NULL);