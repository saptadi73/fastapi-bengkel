
CREATE TABLE accounts (
	id UUID NOT NULL, 
	code VARCHAR(32) NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	normal_balance normalbalance NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	account_type accounttype NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE auth (
	id UUID NOT NULL, 
	user_id UUID NOT NULL, 
	access_token VARCHAR NOT NULL, 
	refresh_token VARCHAR, 
	PRIMARY KEY (id)
)

;


CREATE TABLE booking (
	id UUID NOT NULL, 
	nama VARCHAR NOT NULL, 
	hp VARCHAR NOT NULL, 
	model VARCHAR, 
	type VARCHAR, 
	no_pol VARCHAR, 
	warna VARCHAR, 
	tanggal_booking TIMESTAMP WITHOUT TIME ZONE, 
	vehicle_id UUID, 
	customer_id UUID, 
	created_at DATE DEFAULT now() NOT NULL, 
	updated_at DATE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE brand (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	PRIMARY KEY (id)
)

;


CREATE TABLE category (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	PRIMARY KEY (id)
)

;


CREATE TABLE customer (
	id UUID NOT NULL, 
	nama VARCHAR NOT NULL, 
	hp VARCHAR NOT NULL, 
	alamat VARCHAR, 
	email VARCHAR, 
	tanggal_lahir DATE, 
	created_at DATE DEFAULT now() NOT NULL, 
	updated_at DATE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;


CREATE TABLE expenses (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR NOT NULL, 
	expense_type expensetype NOT NULL, 
	status expensestatus NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	date DATE NOT NULL, 
	bukti_transfer VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE karyawan (
	id UUID NOT NULL, 
	nama VARCHAR NOT NULL, 
	hp VARCHAR NOT NULL, 
	alamat VARCHAR, 
	email VARCHAR NOT NULL, 
	tanggal_lahir DATE, 
	created_at DATE DEFAULT now() NOT NULL, 
	updated_at DATE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;


CREATE TABLE packet_order (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE roles (
	id UUID DEFAULT 'gen_random_uuid()' NOT NULL, 
	name VARCHAR NOT NULL, 
	PRIMARY KEY (id)
)

;


CREATE TABLE satuan (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	PRIMARY KEY (id)
)

;


CREATE TABLE service (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	description VARCHAR, 
	price VARCHAR, 
	cost NUMERIC(10, 2), 
	PRIMARY KEY (id)
)

;


CREATE TABLE supplier (
	id UUID NOT NULL, 
	nama VARCHAR NOT NULL, 
	hp VARCHAR NOT NULL, 
	alamat VARCHAR, 
	email VARCHAR, 
	npwp VARCHAR, 
	perusahaan VARCHAR, 
	toko VARCHAR, 
	created_at DATE DEFAULT now() NOT NULL, 
	updated_at DATE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (email)
)

;


CREATE TABLE users (
	id UUID DEFAULT 'gen_random_uuid()' NOT NULL, 
	username VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	hashed_password VARCHAR NOT NULL, 
	is_active VARCHAR, 
	PRIMARY KEY (id)
)

;


CREATE TABLE attendance (
	id UUID NOT NULL, 
	karyawan_id UUID NOT NULL, 
	date DATE NOT NULL, 
	check_in_time TIME WITHOUT TIME ZONE, 
	check_out_time TIME WITHOUT TIME ZONE, 
	status VARCHAR NOT NULL, 
	notes VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(karyawan_id) REFERENCES karyawan (id)
)

;


CREATE TABLE product (
	id UUID NOT NULL, 
	name VARCHAR NOT NULL, 
	type VARCHAR, 
	description VARCHAR, 
	price NUMERIC(10, 2), 
	cost NUMERIC(10, 2), 
	min_stock NUMERIC(10, 2) NOT NULL, 
	supplier_id UUID, 
	is_consignment BOOLEAN NOT NULL, 
	consignment_commission NUMERIC(10, 2), 
	brand_id UUID, 
	satuan_id UUID, 
	category_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(supplier_id) REFERENCES supplier (id), 
	FOREIGN KEY(brand_id) REFERENCES brand (id), 
	FOREIGN KEY(satuan_id) REFERENCES satuan (id), 
	FOREIGN KEY(category_id) REFERENCES category (id)
)

;


CREATE TABLE purchase_order (
	id UUID NOT NULL, 
	po_no VARCHAR NOT NULL, 
	supplier_id UUID, 
	date DATE NOT NULL, 
	total NUMERIC(10, 2) NOT NULL, 
	pajak NUMERIC(10, 2), 
	pembayaran NUMERIC(10, 2), 
	dp NUMERIC(10, 2), 
	status_pembayaran VARCHAR, 
	status purchaseorderstatus NOT NULL, 
	bukti_transfer VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (po_no), 
	FOREIGN KEY(supplier_id) REFERENCES supplier (id)
)

;


CREATE TABLE role_user (
	id UUID DEFAULT 'gen_random_uuid()' NOT NULL, 
	user_id UUID NOT NULL, 
	role_id UUID NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
)

;


CREATE TABLE service_line_packet_order (
	id UUID NOT NULL, 
	packet_order_id UUID, 
	quantity NUMERIC(10, 2), 
	price NUMERIC(10, 2), 
	discount NUMERIC(10, 2), 
	subtotal NUMERIC(10, 2), 
	service_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(packet_order_id) REFERENCES packet_order (id), 
	FOREIGN KEY(service_id) REFERENCES service (id)
)

;


CREATE TABLE vehicle (
	id UUID NOT NULL, 
	model VARCHAR NOT NULL, 
	brand_id UUID, 
	type VARCHAR NOT NULL, 
	kapasitas VARCHAR NOT NULL, 
	no_pol VARCHAR NOT NULL, 
	tahun NUMERIC NOT NULL, 
	warna VARCHAR NOT NULL, 
	no_mesin VARCHAR, 
	no_rangka VARCHAR, 
	customer_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(brand_id) REFERENCES brand (id), 
	FOREIGN KEY(customer_id) REFERENCES customer (id)
)

;


CREATE TABLE inventory (
	id UUID NOT NULL, 
	product_id UUID, 
	quantity NUMERIC(10, 2) NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;


CREATE TABLE product_cost_history (
	id UUID NOT NULL, 
	product_id UUID, 
	old_cost NUMERIC(10, 2), 
	new_cost NUMERIC(10, 2) NOT NULL, 
	old_quantity NUMERIC(10, 2), 
	new_quantity NUMERIC(10, 2) NOT NULL, 
	purchase_quantity NUMERIC(10, 2), 
	purchase_price NUMERIC(10, 2), 
	calculation_method VARCHAR NOT NULL, 
	notes VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	created_by VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;


CREATE TABLE product_line_packet_order (
	id UUID NOT NULL, 
	packet_order_id UUID, 
	quantity NUMERIC(10, 2), 
	price NUMERIC(10, 2), 
	discount NUMERIC(10, 2), 
	subtotal NUMERIC(10, 2), 
	satuan_id UUID, 
	product_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(packet_order_id) REFERENCES packet_order (id), 
	FOREIGN KEY(satuan_id) REFERENCES satuan (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;


CREATE TABLE product_moved_history (
	id UUID NOT NULL, 
	product_id UUID, 
	type VARCHAR NOT NULL, 
	quantity NUMERIC(10, 2) NOT NULL, 
	timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	performed_by VARCHAR NOT NULL, 
	notes VARCHAR, 
	PRIMARY KEY (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;


CREATE TABLE purchase_order_line (
	id UUID NOT NULL, 
	purchase_order_id UUID, 
	product_id UUID, 
	quantity NUMERIC(10, 2) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	discount NUMERIC(10, 2), 
	subtotal NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_order (id), 
	FOREIGN KEY(product_id) REFERENCES product (id)
)

;


CREATE TABLE workorder (
	id UUID NOT NULL, 
	no_wo VARCHAR NOT NULL, 
	tanggal_masuk TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	tanggal_keluar TIMESTAMP WITHOUT TIME ZONE, 
	keluhan VARCHAR NOT NULL, 
	kilometer NUMERIC(10, 2), 
	saran VARCHAR, 
	status VARCHAR NOT NULL, 
	total_discount NUMERIC(10, 2), 
	total_biaya NUMERIC(10, 2) NOT NULL, 
	pajak NUMERIC(10, 2), 
	keterangan VARCHAR, 
	status_pembayaran VARCHAR, 
	dp NUMERIC(10, 2), 
	next_service_date DATE, 
	next_service_km NUMERIC(10, 2), 
	karyawan_id UUID, 
	customer_id UUID, 
	vehicle_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(karyawan_id) REFERENCES karyawan (id), 
	FOREIGN KEY(customer_id) REFERENCES customer (id), 
	FOREIGN KEY(vehicle_id) REFERENCES vehicle (id)
)

;


CREATE TABLE journal_entries (
	id UUID NOT NULL, 
	entry_no VARCHAR(40) NOT NULL, 
	date DATE NOT NULL, 
	memo VARCHAR(255), 
	journal_type journaltype NOT NULL, 
	customer_id UUID, 
	supplier_id UUID, 
	workorder_id UUID, 
	purchase_id UUID, 
	created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	created_by VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(customer_id) REFERENCES customer (id), 
	FOREIGN KEY(supplier_id) REFERENCES supplier (id), 
	FOREIGN KEY(workorder_id) REFERENCES workorder (id), 
	FOREIGN KEY(purchase_id) REFERENCES purchase_order (id)
)

;


CREATE TABLE product_ordered (
	id UUID NOT NULL, 
	quantity NUMERIC(10, 2) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	discount NUMERIC(10, 2), 
	satuan_id UUID, 
	product_id UUID, 
	workorder_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(satuan_id) REFERENCES satuan (id), 
	FOREIGN KEY(product_id) REFERENCES product (id), 
	FOREIGN KEY(workorder_id) REFERENCES workorder (id)
)

;


CREATE TABLE service_ordered (
	id UUID NOT NULL, 
	quantity NUMERIC(10, 2) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	discount NUMERIC(10, 2), 
	service_id UUID, 
	workorder_id UUID, 
	PRIMARY KEY (id), 
	FOREIGN KEY(service_id) REFERENCES service (id), 
	FOREIGN KEY(workorder_id) REFERENCES workorder (id)
)

;


CREATE TABLE journal_lines (
	id UUID NOT NULL, 
	entry_id UUID NOT NULL, 
	account_id UUID NOT NULL, 
	description VARCHAR(255), 
	debit NUMERIC(18, 2) NOT NULL, 
	credit NUMERIC(18, 2) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT chk_journal_lines_debit_nonneg CHECK (debit >= 0), 
	CONSTRAINT chk_journal_lines_credit_nonneg CHECK (credit >= 0), 
	CONSTRAINT chk_one_side_positive CHECK ((debit = 0 AND credit > 0) OR (credit = 0 AND debit > 0)), 
	FOREIGN KEY(entry_id) REFERENCES journal_entries (id) ON DELETE CASCADE, 
	FOREIGN KEY(account_id) REFERENCES accounts (id)
)

;

